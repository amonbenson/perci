"""
This module contains the core functionality of the library.
"""

from typing import Optional
from .node import Node, RootNode


def perci(data: Optional[dict] = None, root_key: str = "root") -> RootNode:
    """
    Creates a Perci state tree from a dictionary.
    """

    if data is None:
        data = {}

    return RootNode.from_dict(data, root_key)
