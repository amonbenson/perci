from typing import Any
from collections.abc import MutableSequence
from .node import ReactiveNode
from .types import UnpackedType, AtomicType


class ReactiveListNode(ReactiveNode, MutableSequence):
    def get_value_repr(self) -> str:
        return "list"

    def _index_to_key(self, index: int, check_bounds: bool = True) -> str:
        # handle negative indices
        if index < 0:
            index += len(self)

        # check if the index is out of bounds
        if check_bounds and not (0 <= index < len(self._children)):
            raise IndexError(f"Index {index} out of bounds")

        # convert the index to a string key
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
        """
        let n = [x0, x1, x2, x3, x4, x5]
        ==> n._children = {
                "0": x0,
                "1": x1,
                "2": x2,
                "3": x3,
                "4": x4,
                "5": x5,
            }

        del n[2]

        ==> del n._children["2"]

            let x3 = n._children["3"].pop()
            x3.set_key("2")
            add n._children["2"] = x3

            let x4 = n._children["4"]
            x4.set_key("3")
            add n._children["3"] = x4

        ==> n._children ={
                "0": x0,
                "1": x1,
                "2": x3,
                "3": x4,
                "4": x5,
            }
        """
        key = self._index_to_key(index)
        self.remove_child(key)

        # reindex the remaining children. Note that length is already decreased by 1. Also, index can be negative so we use the converted key
        for i in range(int(key) + 1, len(self) + 1):
            child = self.remove_child(str(i))
            child.set_key(str(i - 1))
            self.add_child(child)

    def __len__(self) -> int:
        return len(self._children)

    def __contains__(self, key: Any) -> bool:
        if isinstance(key, ReactiveNode):
            return any(child is key for child in self._children.values())
        elif isinstance(key, AtomicType):
            return any(child.is_leaf() and child.unpack() == key for child in self._children.values())
        else:
            return False

    def insert(self, index: int, value: Any):
        key = self._index_to_key(index, check_bounds=False)

        # reindex the children after the insertion point. Note that we need to iterate in reverse order
        for i in range(len(self), index, -1):
            child = self.remove_child(str(i - 1))
            child.set_key(str(i))
            self.add_child(child)

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
