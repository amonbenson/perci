"""
This module is the entry point for the package.
"""

from typing import Optional
from .namespace import ReactiveNamespace
from .node import ReactiveNode
from .dict_node import ReactiveDictNode


def create_root_node(root_key: str = "root") -> ReactiveNode:
    """
    Creates an empty reactive tree containing only the root node.

    :param root_key: The key of the root node. Defaults to "root".

    :return: The root node of the reactive tree.
    """

    node = ReactiveNode(root_key)
    namespace = ReactiveNamespace(node)
    node.set_namespace(namespace, [root_key])

    return node


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

    node = ReactiveDictNode(root_key)
    namespace = ReactiveNamespace(node)
    node.set_namespace(namespace, [root_key])

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
