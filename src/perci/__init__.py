"""
This module is the entry point for the package.
"""

from typing import Optional
from .node import ReactiveNode
from .namespace import ReactiveNamespace


def reactive(data: Optional[dict] = None, root_key: str = "root") -> ReactiveNode:
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

    if data:
        raise NotImplementedError("Converting from a dictionary is not supported yet")

    root_node = ReactiveNode(root_key)
    namespace = ReactiveNamespace(root_node)
    root_node.set_namespace(namespace, [])

    return root_node
