import threading
from .changes import Change


def path_matches(pattern: list[str], path: list[str], allow_children: bool = False) -> bool:
    """
    Return whether a given path matches a pattern.

    :param pattern: The pattern to match.
    :param path: The path to match.
    :param allow_children: Whether to allow the pattern to match children of the path.

    The pattern may contain a wildcard "*" to match any part of the path.
    When `len(path) < len(pattern)`, the result is always `False`.
    When `len(path) > len(pattern)`, the result is `True` if and only if `allow_children` is `True`.
    """

    if len(path) < len(pattern):
        return False

    # truncate the pattern if it is longer than the path and children are allowed
    if len(path) > len(pattern):
        if allow_children:
            path = path[: len(pattern)]
        else:
            return False

    # return true if all parts of the pattern match the path. The pattern may contain a wildcard "*"
    return all(pattern[i] == path[i] or pattern[i] == "*" for i in range(len(pattern)))


class Watcher:
    def __init__(self, path: list[str], handler: callable = None):
        self.path = path
        self.handler = handler

    def invoke(self, change: Change):
        if path_matches(self.path, change.path, allow_children=True):
            self.handler(change)

    def __str__(self):
        return f"{self.__class__.__name__}(path={self.path})"

    def __repr__(self):
        return str(self)


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
