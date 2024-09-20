from typing import Any
from collections.abc import MutableSequence
from .node import ReactiveNode
from .types import UnpackedType, AtomicType


class ReactiveListNode(ReactiveNode, MutableSequence):
    def get_value_repr(self) -> str:
        return "list"

    def _index_to_key(self, index: int, check_bounds: bool = True) -> str:
        if check_bounds and not (0 <= index < len(self._children)):
            raise IndexError(f"Index {index} out of bounds")

        return str(index)

    def _check_key_consistency(self):
        for i, key in enumerate(self._children.keys()):
            if key != self._index_to_key(i, check_bounds=False):
                raise ValueError(f"Key {key} does not match index {i}")

    def __getitem__(self, index: int | slice) -> UnpackedType:
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(len(self)))]

        key = self._index_to_key(index)
        return self._children[key].unpack()

    def __setitem__(self, index: int, value: Any):
        key = self._index_to_key(index)

        old_child = self._children[key]

        # if the old child is a leaf node and the new value is an atomic type, update the value directly
        if old_child.is_leaf() and isinstance(value, AtomicType):
            old_child.set_value(value)
            return

        # remove the old child
        self.remove_child(key)

        # use the generic pack method to add the new child
        self.pack(key, value)

    def __delitem__(self, index: int):
        key = self._index_to_key(index)
        self.remove_child(key)

        # update the keys of the remaining children
        for i in range(index + 1, len(self)):
            self._children[self._index_to_key(i)].set_key(str(i - 1))

    def __len__(self) -> int:
        return len(self._children)

    def __contains__(self, index: int) -> bool:
        try:
            self._index_to_key(index)
            return True
        except IndexError:
            return False

    def insert(self, index: int, value: Any):
        key = self._index_to_key(index, check_bounds=False)

        # update the keys of the remaining children
        for i in range(index, len(self)):
            self._children[self._index_to_key(i)].set_key(str(i + 1))

        self.pack(key, value)

    def json(self) -> Any:
        return [child.json() for child in self._children.values()]

    def __str__(self) -> str:
        return f"ReactiveListNode([{', '.join(str(child) for child in self._children.values())}])"

    def unpack(self) -> "ReactiveListNode":
        return self

    def pack_list(self, key: str, data: list):
        child = ReactiveListNode(key)
        self.add_child(child)

        # invoke the generic pack method for each item in the list
        for i, item in enumerate(data):
            child.pack(str(i), item)


ReactiveNode.PACK_METHODS[list] = ReactiveListNode.pack_list
