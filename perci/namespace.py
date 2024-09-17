"""
Provides a class to group reactive nodes into a single thread-safe namespace.
"""

import threading
from typing import TYPE_CHECKING
from .watcher import Watcher, path_matches
from .changes import Change

if TYPE_CHECKING:
    from .node import ReactiveNode


class ReactiveNamespace:
    """
    Represents a reactive tree namespace.

    :param root_node: The root node of the namespace.
    """

    def __init__(self, root_node: "ReactiveNode"):
        self.root = root_node
        self.lock = threading.Lock()

        self._watchers: list[Watcher] = []

    def add_watcher(self, watcher: Watcher):
        self._watchers.append(watcher)

    def remove_watcher(self, watcher: Watcher):
        self._watchers.remove(watcher)

    def remove_watcher_by_path(self, path: list[str]):
        self._watchers = [watcher for watcher in self._watchers if not path_matches(path, watcher.path, allow_children=True)]

    def invoke_watcher(self, change: Change):
        for watcher in self._watchers:
            watcher.invoke(change)

    def get_watchers(self) -> list[Watcher]:
        return self._watchers
