"""
Provides classes for tracking changes in a reactive tree.
"""

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
    repr: str
    value: Any

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
