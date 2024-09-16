"""
Provides a class to group reactive nodes into a single thread-safe namespace.
"""

import threading
from typing import TYPE_CHECKING
from .changes import ChangeTracker

if TYPE_CHECKING:
    from .node import ReactiveNode


class ReactiveNamespace:
    """
    Represents a reactive tree namespace.

    :param root_node: The root node of the namespace.
    """

    def __init__(self, root_node: "ReactiveNode"):
        self.root = root_node
        self.change_tracker = ChangeTracker()
        self.lock = threading.Lock()
