"""
Provides classes for tracking changes in a reactive tree.
"""

import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Change:
    """
    Represents a single change in a reactive tree.

    :param change_type: The type of change that occurred.
    :param path: The path under which the change occurred.
    """

    change_type: str = field(init=False)
    path: list[str]


@dataclass
class AddChange(Change):
    """
    Represents an addition change in a reactive tree.

    :param key: The key of the added child.
    """

    key: str

    def __post_init__(self):
        self.change_type = "add"


@dataclass
class RemoveChange(Change):
    """
    Represents a removal change in a reactive tree.

    :param key: The key of the removed child.
    """

    key: str

    def __post_init__(self):
        self.change_type = "remove"


@dataclass
class UpdateChange(Change):
    """
    Represents an update change in a reactive tree.

    :param value: The new value of the node.
    """

    value: Any

    def __post_init__(self):
        self.change_type = "update"


class ChangeTracker:
    """
    Tracks changes in a reactive tree.
    """

    def __init__(self):
        self._changes: list[Change] = []
        self._access_lock = threading.Lock()

    def push_change(self, change: Change):
        """
        Adds a change to the tracker.

        :param change: The change to push.
        """

        with self._access_lock:
            self._changes.append(change)

    def get_changes(self) -> list[Change]:
        """
        Retrieves all changes from the tracker.

        :return: A list of changes.

        The changes are cleared from the tracker after retrieval.
        """

        with self._access_lock:
            changes = self._changes
            self._changes = []
            return changes
