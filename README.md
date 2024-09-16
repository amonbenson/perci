# Perci - A simple reactive state management library

```python
import threading
from dataclasses import dataclass
from typing import Any

@dataclass
class Change:
    change_type: str = None
    path: list[str]

@dataclass
class AddChange(Change):
    key: str

    def __post_init__(self):
        self.change_type = "add"

@dataclass
class RemoveChange(Change):
    key: str

    def __post_init__(self):
        self.change_type = "remove"

@dataclass
class UpdateChange(Change):
    value: Any

    def __post_init__(self):
        self.change_type = "update"

class ChangeTracker:
    def __init__(self):
        self._changes: list[Change] = []
        self._access_lock = threading.Lock()

    def push_change(self, change: Change):
        with self._access_lock:
            self._changes.append(change)

    def get_changes(self) -> list[Change]:
        with self._access_lock:
            changes = self._changes
            self._changes = []
            return changes
```

```python
import threading

class ReactiveTree:
    def __init__(self, root_key: str = "root"):
        self.root = ReactiveNode(root_key)
        self.change_tracker = ChangeTracker()
        self._access_lock = threading.Lock()

    def get_access_lock(self) -> threading.Lock:
        return self._access_lock
```

```python
from contextlib import nullcontext
from typing import Any, Optional

class ReactiveNode:
    def __init__(self, key: str):
        self._key: str = key
        self._value: Any = None

        self._children: dict[str, ReactiveNode] = {}
        self._parent: Optional[ReactiveNode] = None

        self._tree: Optional[ReactiveTree] = None
        self._path: list[str] = []

    def _tree_lock(self):
        if not self._tree:
            raise Exception("Node is not part of a reactive tree")

        return self._tree.get_access_lock()

    def get_key(self) -> str:
        return self._key

    def get_value(self) -> Any:
        return self._value

    def set_value(self, value: Any):
        with self._tree_lock() if self._tree else nullcontext():
            if self._value == value:
                return

            self._value = value
            self._tree.change_tracker.push_change(UpdateChange(path=self._path, value=value))

    def add_child(self, child: "ReactiveNode"):
        with self._tree.get_access_lock():
            if child.get_key() in self._children:
                raise Exception("Child already exists")
            if child.get_parent():
                raise Exception("Child already has a parent")

            self._children[child.get_key()] = child
            child._parent = self  # pylint: disable=protected-access
            child.set_tree(self._tree, self._path + [child.get_key()])

            self._tree.change_tracker.push_change(AddChange(path=self._path, key=child.get_key()))

    def remove_child(self, key: str):
        with self._tree.get_access_lock():
            if key not in self._children:
                raise Exception("Child does not exist")

            child = self._children.pop(key)
            child._parent = None  # pylint: disable=protected-access
            child.set_tree(None, [])

            self._tree.change_tracker.push_change(RemoveChange(path=self._path, key=key))

    def has_child(self, key: str) -> bool:
        return key in self._children

    def get_child(self, key: str) -> Optional["ReactiveNode"]:
        return self._children.get(key)

    def get_tree(self) -> Optional["ReactiveTree"]:
        return self._tree

    def set_tree(self, tree: "ReactiveTree", path: list[str]):
        self._tree = tree
        self._path = path

        # update children recursively
        for key, child in self._children.items():
            child.set_tree(tree, path + [key])
```

```python
class ReactiveDict(ReactiveNode):
    def __init__(self):
        pass
```
