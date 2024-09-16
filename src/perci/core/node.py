"""
This module defines the Node class, which is the building block of the tree structure.
"""

import re
import threading
from typing import Any, Optional
from contextlib import nullcontext
from .changes import ChangeTracker

AtomicType = (int, float, str, bool)


class Node:
    """
    A node in the tree structure.

    :param key: The key of the node.
    """

    def __init__(self, key: str):
        self._validate_key(key)

        self._key = key
        self._path: list[str] = [key]

        self._parent: Optional["Node"] = None
        self._children: dict[str, "Node"] = {}
        self._root: Optional["RootNode"] = None

        self._value: Any = None
        self._children_changed = False

    def _validate_key(self, key: str):
        if not re.match(r"^[a-zA-Z0-9_-]+$", key):
            raise ValueError(f"Invalid key {key}")

    def is_root(self):
        """
        Return True if the node is the root node.
        """

        return self._root == self

    def is_leaf(self):
        """
        Return True if the node is a leaf node.
        """

        return not self._children

    def _update_root(self, root: "RootNode"):
        self._root = root

        for child in self._children.values():
            child._update_root(root)  # pylint: disable=protected-access

    def _update_path(self, path: list[str]):
        self._path = path

        for child in self._children.values():
            child._update_path(path + [child._key])  # pylint: disable=protected-access

    def _try_register_change(self, change_type: str, path: list[str], **kwargs):
        if self._root:
            self._root.get_change_tracker().register(change_type, path, **kwargs)

    def add_child(self, child: "Node"):
        """
        Add a node as a child of this node.

        :param child: The child node to add.
        """

        with self.get_root().get_lock() if self.get_root() else nullcontext():
            if child.get_key() in self._children:
                raise ValueError(f"Child with id {child.get_key()} already exists")
            if child.get_parent() is not None:
                raise ValueError("Child already has a parent")

            # pylint: disable=protected-access
            self._children[child._key] = child
            child._parent = self
            child._update_path(self._path + [child._key])
            child._update_root(self._root)

            self._try_register_change("add", child.get_path())

    def remove_child(self, child_id: str):
        """
        Remove a child node from this node.
        """

        with self.get_root().get_lock() if self.get_root() else nullcontext():
            if child_id not in self._children:
                raise ValueError(f"Child with id {child_id} does not exist")

            child = self._children.pop(child_id)

            self._try_register_change("remove", child.get_path())

            # pylint: disable=protected-access
            child._parent = None
            child._update_path([child._key])
            child._update_root(None)

    def has_child(self, key: str) -> bool:
        """
        Return True if the node has a child with the given key.
        """

        return key in self._children

    def get_child(self, key: str):
        """
        Get a child node with the given key.
        """

        return self._children[key]

    def get_children(self):
        """
        Return the children of the node.
        """

        return self._children

    def set_value(self, value):
        """
        Set the value of the node.
        """

        with self.get_root().get_lock() if self.get_root() else nullcontext():
            if self._value == value:
                return

            self._value = value

            self._try_register_change("update", self._path, value=value)

    def get_value(self):
        """
        Get the value of the node.
        """

        with self.get_root().get_lock() if self.get_root() else nullcontext():
            return self._value

    def get_root(self) -> Optional["RootNode"]:
        """
        Get the root node of the tree or None if the node is not part of a tree.
        """

        return self._root

    def get_parent(self) -> Optional["Node"]:
        """
        Get the parent node of this node or None if the node is the root node.
        """

        return self._parent

    def get_path(self) -> list[str]:
        """
        Get the path of the node within the tree.
        """

        return self._path

    def get_key(self) -> str:
        """
        Get the key of the node.
        """

        return self._key

    def print_tree(self, indent: int = 2, level: int = 0):
        """
        Print the tree structure starting from this node.
        """

        print(f"{' ' * indent * level}{self._key}: {self._value}")
        for child in self._children.values():
            child.print_tree(indent, level + 1)

    def print_changes(self):
        """
        Print the changes that have occurred in the tree.
        """

        for change in self._root.get_changes():
            print(change)

    def _unpack(self):
        if self.is_leaf():
            return self._value
        else:
            return self

    def __getitem__(self, key: str) -> Any:
        """
        Get the value of a child node with the given key.

        :param key: The key of the child node.

        :return: The value of the child node.
            If the child node is a leaf node, its value is returned.
            Otherwise, a reference to the child node is returned.
        """

        # handle the case where the key is a path
        if "." in key:
            path = key.split(".")
            if path[0] not in self._children:
                raise KeyError(f"Child with id {path[0]} does not exist")
            return self.get_child(path[0]).__getitem__(".".join(path[1:]))

        if key not in self._children:
            raise KeyError(f"Child with id {key} does not exist")
        return self.get_child(key)._unpack()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the value of a child node with the given key.

        :param key: The key of the child node.
        :param default: The default value to return if the child node does not exist.

        :return: The value of the child node as returned by __getitem__ or the default value, if the child node does not exist.
        """

        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key: str, value: Any):
        """
        Set the value of a child node with the given key.

        :param key: The key of the child node.
        :param value: The value to set.
            If the value is an atomic type, the child node is created as a leaf node.
            If the value is a dictionary, the child node is created as a non-leaf node and its children are added recursively.
        """

        # handle the case where the key is a path
        if "." in key:
            path = key.split(".")
            if path[0] not in self._children:
                raise KeyError(f"Child with id {path[0]} does not exist")
            self.get_child(path[0]).__setitem__(".".join(path[1:]), value)
            return

        # validate the value type
        if not isinstance(value, (AtomicType, dict)):
            raise ValueError(f"Unsupported type {type(value)}")

        # handle the old child: either update its value or remove it
        if self.has_child(key):
            child = self.get_child(key)

            if child.is_leaf() and isinstance(value, AtomicType):
                # if the child is a leaf node and the value is an atomic type, only set the value
                child.set_value(value)
                return
            else:
                # otherwise, remove the old child
                self.remove_child(key)

        # add the new child
        if isinstance(value, AtomicType):
            child = Node(key)
            self.add_child(child)

            # set the value of the child
            child.set_value(value)
        elif isinstance(value, dict):
            child = Node(key)
            self.add_child(child)

            # add more children recursively
            for k, v in value.items():
                child[k] = v
        else:
            raise ValueError(f"Unsupported type {type(value)}")

    def __delitem__(self, key: str):
        if key not in self._children:
            raise KeyError(f"Child with id {key} does not exist")

        self.remove_child(key)

    def keys(self):
        """
        Return the keys of the children.
        """

        return self._children.keys()

    def values(self):
        """
        Return the unpacked values of the children.
        """

        # pylint: disable=protected-access
        return [child._unpack() for child in self._children.values()]

    def items(self):
        """
        Return the unpacked items of the children.
        """

        # pylint: disable=protected-access
        return [(key, child._unpack()) for key, child in self._children.items()]

    def clear(self):
        """
        Remove all children.
        """

        for key in list(self._children.keys()):
            del self[key]

    def pop(self, key: str, default: Any = None) -> Any:
        """
        Remove a child node with the given key and return its value.

        :param key: The key of the child node.
        :param default: The default value to return if the child node does not exist.

        :return: The value of the child node.
        """

        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            return default

    def popitem(self) -> tuple[str, Any]:
        """
        Remove the last child node and return its key and value.

        :return: A tuple containing the key and value of the child node.
        """

        if not self._children:
            raise KeyError("popitem(): dictionary is empty")

        # pop the last child
        key = next(reversed(self._children))
        value = self.pop(key)
        return (key, value)

    def setdefault(self, key: str, default: Any = None) -> Any:
        """
        Get the value of a child node with the given key.
        If the child node does not exist, create it with the default value.

        :param key: The key of the child node.
        :param default: The default value to set if the child node does not exist.

        :return: The value of the child node.
        """

        if key in self._children:
            return self[key]
        self[key] = default
        return default

    def update(self, data: "dict | Node"):
        """
        Update the node with the given data.

        :param data: The data to update the node with.
            If the data is a dictionary, the node is updated with the dictionary.
            If the data is a Node, the node is updated with the Node's dictionary.
        """

        if isinstance(data, Node):
            data = data.as_dict()

        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        for key, value in data.items():
            self[key] = value

    def as_dict(self):
        """
        Return the node as a dictionary. All children will be unpacked recursively.
        """

        if self.is_leaf():
            return self._value
        else:
            return {key: child.as_dict() for key, child in self._children.items()}


class RootNode(Node):
    """
    A special node that represents the root of the tree structure.

    :param key: The key of the root node.
    """

    def __init__(self, key: str):
        super().__init__(key)

        self._root = self
        self._change_tracker = ChangeTracker()

        self._lock = threading.Lock()

    def get_change_tracker(self) -> ChangeTracker:
        """
        Get the change tracker of the root node.
        """

        return self._change_tracker

    def get_changes(self) -> ChangeTracker:
        """
        Get the changes that have occurred in the tree.
        """

        return self._change_tracker.get_changes()

    def get_lock(self) -> threading.Lock:
        """
        Get the lock of the root node.
        """

        return self._lock

    @staticmethod
    def from_dict(data: dict, root_key: str = "root") -> "RootNode":
        """
        Create a RootNode from a dictionary.

        :param data: The dictionary to create the RootNode from.
        :param root_key: The key of the root node.

        :return: The created RootNode.
        """

        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        root = RootNode(root_key)
        root.update(data)
        return root
