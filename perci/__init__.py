"""
This module is the entry point for the package.
"""

from typing import Optional
from .namespace import ReactiveNamespace
from .node import ReactiveNode, AtomicType
from .dict_node import ReactiveDictNode
from .list_node import ReactiveListNode
from .watcher import Watcher, QueueWatcher


def _create_node(cls: type[ReactiveNode], *args, **kwargs) -> ReactiveNode:
    """
    Creates a new namespace with a single root node.

    :param cls: The class of the node
    :param args: The positional arguments to pass to the node
    :param kwargs: The keyword arguments to pass to the node
    """

    node = cls(*args, **kwargs)
    namespace = ReactiveNamespace(node)
    node.set_namespace(namespace, [node.get_key()])

    return node


def create_root_node(root_key: str = "root") -> ReactiveNode:
    """
    Creates an empty reactive tree containing only the root node.

    :param root_key: The key of the root node. Defaults to "root".

    :return: The root node of the reactive tree.
    """

    return _create_node(ReactiveNode, root_key)


def create_dict_node(data: Optional[dict] = None, root_key: str = "root") -> ReactiveNode:
    """
    Creates a reactive tree from the given data.

    :param data: The data to create the tree from.
    :param root_key: The key of the root node. Defaults to "root".

    :return: The root node of the reactive tree.
    """

    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")

    node = _create_node(ReactiveDictNode, root_key)

    # pack the data into the root node
    for key, value in data.items():
        node.pack(key, value)

    return node


def reactive(data: Optional[dict] = None, root_key: str = "root") -> ReactiveNode:
    """
    Creates a reactive tree from the given data.

    :param data: The data to create the tree from.
    :param root_key: The key of the root node. Defaults to "root".

    :return: The root node of the reactive tree.
    """

    return create_dict_node(data, root_key)


def _create_watcher(node: ReactiveNode, path: str, cls: type[Watcher], *args, **kwargs) -> Watcher:
    """
    Creates a watcher of the given type.

    :param node: The node to watch.
    :param path: The path to watch.
    :param cls: The base class of the watcher.
    :param args: The positional arguments to pass to the watcher constructor.
    :param kwargs: The keyword arguments to pass to the watcher constructor.
    """

    if not isinstance(node, ReactiveNode):
        info_message = f"Cannot watch value of type {type(node)}."
        if isinstance(node, AtomicType):
            info_message += f' Use node.get_child("<key>") instead of node["<key>"] if you want to watch an atomic value.'
        raise ValueError(info_message)

    absolute_path = node.get_path() + (path.split(".") if path else [])
    watcher = cls(absolute_path, *args, **kwargs)
    node.get_namespace().add_watcher(watcher)
    return watcher


def create_watcher(node: ReactiveNode, handler: callable, path: str = "") -> Watcher:
    """
    Creates a watcher that calls the given handler when a change occurs.

    :param node: The node to watch.
    :param handler: The handler to call when a change occurs.
    :param path: The path to watch. Defaults to None.
    """

    return _create_watcher(node, path, Watcher, handler)


def create_queue_watcher(node: ReactiveNode, path: str = "") -> QueueWatcher:
    """
    Creates a thread-safe watcher that stores changes in a queue.

    :param node: The node to watch.
    :param path: The path to watch. Defaults to None.
    """

    return _create_watcher(node, path, QueueWatcher)


def watch(node: ReactiveNode, handler: callable, path: str = "") -> Watcher:
    """
    Adds a watcher to the given node.

    :param node: The node to watch.
    :param handler: The handler to call when a change occurs.
    :param path: The path to watch. Defaults to None.
    """

    return create_watcher(node, handler, path)
