import threading
from .changes import Change


def path_matches(pattern: list[str], path: list[str], allow_children: bool = False) -> bool:
    # if children are allowed, only the first part of the path must match
    if len(path) > len(pattern) and allow_children:
        path = path[: len(pattern)]

    # return true if all parts of the pattern match the path. The pattern may contain a wildcard "*"
    return all(pattern[i] == path[i] or pattern[i] == "*" for i in range(len(pattern)))


class Watcher:
    def __init__(self, path: list[str], handler: callable = None):
        self.path = path
        self.handler = handler

    def invoke(self, change: Change):
        if not path_matches(self.path, change.path, allow_children=True):
            self.handler(change)


class QueueWatcher(Watcher):
    def __init__(self, path_pattern: list[str]):
        super().__init__(path_pattern, self._on_change)

        self._changes: list[Change] = []
        self._lock = threading.Lock()

    def _on_change(self, change: Change):
        self._changes.append(change)

    def invoke(self, change: Change):
        with self._lock:
            super().invoke(change)

    def get_changes(self) -> list[Change]:
        with self._lock:
            changes = self._changes
            self._changes = []
            return changes
