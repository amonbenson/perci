from typing import Any
from .node import ReactiveNode, AtomicType, UnpackedType


class ReactiveDictNode(ReactiveNode):
    def _invoke_nested_key_method(self, key: str, method: callable, *args, **kwargs) -> Any:
        path = key.split(".")
        if path[0] not in self._children:
            raise KeyError(f"Key {path[0]} not found")

        return method(self._children[path[0]], ".".join(path[1:]), *args, **kwargs)

    def __getitem__(self, key: str) -> UnpackedType:
        if "." in key:
            self._invoke_nested_key_method(key, ReactiveDictNode.__getitem__)
            return

        if key not in self._children:
            raise KeyError(f"Key {key} not found")

        return self._children[key].unpack()

    def __setitem__(self, key: str, value: Any):
        if "." in key:
            self._invoke_nested_key_method(key, ReactiveDictNode.__setitem__, value)
            return

        if old_child := self._children.get(key):
            # if the old child is a leaf node and the new value is an atomic type, update the value directly
            if old_child.is_leaf() and isinstance(value, AtomicType):
                old_child.set_value(value)
                return

            # remove the old child
            self.remove_child(key)

        # use the generic pack method to add the new child
        self.pack(key, value)

    def __delitem__(self, key: str):
        if "." in key:
            self._invoke_nested_key_method(key, ReactiveDictNode.__delitem__)
            return

        if key not in self._children:
            raise KeyError(f"Key {key} not found")

        self.remove_child(key)

    def __contains__(self, key: str) -> bool:
        if "." in key:
            return self._invoke_nested_key_method(key, ReactiveDictNode.__contains__)

        return key in self._children

    def get(self, key: str, default: Any = None) -> UnpackedType:
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> list[str]:
        return list(self._children.keys())

    def values(self) -> list[UnpackedType]:
        return [child.unpack() for child in self._children.values()]

    def items(self) -> list[tuple[str, UnpackedType]]:
        return [(key, child.unpack()) for key, child in self._children.items()]

    def clear(self):
        for key in self.keys():
            self.remove_child(key)

    def update(self, data: dict):
        for k, v in data.items():
            self[k] = v

    def pop(self, key: str, default: Any = None) -> UnpackedType:
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            return default

    def popitem(self) -> tuple[str, UnpackedType]:
        key = next(iter(self.keys()))
        value = self.pop(key)
        return key, value

    def setdefault(self, key: str, default: Any = None) -> UnpackedType:
        if key not in self:
            self[key] = default

        return self[key]

    def pack_dict(self, key: str, data: dict):
        child = ReactiveDictNode(key)
        self.add_child(child)

        # invoke the generic pack method for each key-value pair
        for k, v in data.items():
            self.pack(k, v)


ReactiveNode.PACK_METHODS[dict] = ReactiveDictNode.pack_dict
