"""
Provides a class to represent a node in a reactive tree.
"""

import re
import threading
from contextlib import nullcontext
from typing import Any, Optional, ContextManager
from .namespace import ReactiveNamespace
from .changes import AddChange, RemoveChange, UpdateChange


class MissingNamespaceError(Exception):
    """
    Raised when a function is called that requires a namespace, but the node does not have one.
    """


class ReactiveNode:
    """
    Represents a node in a reactive tree.

    :param key: The key of the node.

    :raises ValueError: If the key is invalid.
    """

    def __init__(self, key: str):
        self._key: str = key
        if not self.is_key_valid(key):
            raise ValueError(f"Key {key} is invalid")

        self._value: Any = None

        self._children: dict[str, ReactiveNode] = {}
        self._parent: Optional[ReactiveNode] = None

        self._namespace: Optional[ReactiveNamespace] = None
        self._path: list[str] = [self._key]

    @staticmethod
    def is_key_valid(key: str) -> bool:
        """
        Returns whether the given key is valid.

        :param key: The key to check.
        """

        return bool(re.match(r"^[a-zA-Z0-9_-]+$", key))

    def _namespace_lock(self) -> threading.Lock:
        """
        Returns the lock of the namespace of the node.

        :raises MissingNamespaceError: If the node is not part of a namespace.

        :return: The lock of the namespace.
        """

        if not self._namespace:
            raise MissingNamespaceError("Node is not part of a namespace")

        return self._namespace.lock

    def _optional_namespace_lock(self) -> ContextManager:
        """
        Returns the lock of the namespace of the node if it exists.

        :return: The lock of the namespace or a null context manager.
        """

        return self._namespace.lock if self._namespace else nullcontext()

    def get_key(self) -> str:
        """
        Returns the key of this node.
        """

        return self._key

    def get_value(self) -> Any:
        """
        Returns the value of the node.
        """

        return self._value

    def set_value(self, value: Any):
        """
        Sets the value of the node.

        :param value: The new value of the node.
        """

        with self._optional_namespace_lock():
            if self._value == value:
                return

            self._value = value
            self._namespace.change_tracker.push_change(UpdateChange(path=self._path, value=value))

    def add_child(self, child: "ReactiveNode"):
        """
        Adds a child to the node.

        :param child: The child to add.

        :raises KeyError: If the child already exists.
        :raises ValueError: If the child already has a parent.
        """

        with self._namespace_lock():
            if child.get_key() in self._children:
                raise KeyError(f"Child {child.get_key()} already exists")
            if child.get_parent():
                raise ValueError(f"Child {child.get_key()} already has a parent")

            self._children[child.get_key()] = child
            child._parent = self  # pylint: disable=protected-access
            child.set_namespace(self._namespace, self._path + [child.get_key()])

            self._namespace.change_tracker.push_change(AddChange(path=self._path, key=child.get_key()))

    def remove_child(self, key: str):
        """
        Removes a child from the node.

        :param key: The key of the child to remove.

        :raises KeyError: If the child does not exist.
        """

        with self._namespace_lock():
            if key not in self._children:
                raise KeyError(f"Child {key} does not exist")

            child = self._children.pop(key)
            child._parent = None  # pylint: disable=protected-access
            child.set_namespace(None, [])

            self._namespace.change_tracker.push_change(RemoveChange(path=self._path, key=key))

    def has_child(self, key: str) -> bool:
        """
        Returns whether the node has a child with the given key.

        :param key: The key of the child to check for.
        """

        return key in self._children

    def get_child(self, key: str) -> Optional["ReactiveNode"]:
        """
        Returns the child with the given key.

        :param key: The key of the child to get.

        :return: The child node or None if it does not exist.
        """

        return self._children.get(key)

    def get_parent(self) -> Optional["ReactiveNode"]:
        """
        Returns the parent of the node.
        """

        return self._parent

    def get_namespace(self) -> Optional[ReactiveNamespace]:
        """
        Returns the namespace of the node.
        """

        return self._namespace

    def set_namespace(self, namespace: ReactiveNamespace, path: list[str]):
        """
        Sets the namespace of the node.

        :param namespace: The new namespace of the node.
        :param path: The path of the node in the namespace.

        :raises ValueError: If the node is already part of a namespace.
        """

        if self._namespace:
            raise ValueError(f"Node {self.get_absolute_key()} is already part of a namespace")

        self._namespace = namespace
        self._path = path

        # update children recursively
        for key, child in self._children.items():
            child.set_namespace(namespace, path + [key])

    def get_path(self) -> list[str]:
        """
        Returns the path of the node in the namespace.
        """

        return self._path

    def is_leaf(self) -> bool:
        """
        Returns whether the node is a leaf node.
        """

        return not self._children

    def is_root(self) -> bool:
        """
        Returns whether the node is the root node.
        """

        return self._parent is None

    def __str__(self) -> str:
        return f"ReactiveNode({self._key})"

    def __repr__(self) -> str:
        return str(self)
