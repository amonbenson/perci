from typing import Any
from .node import ReactiveNode, AtomicType, UnpackedType


class ReactiveDictNode(ReactiveNode):
    def get_value_repr(self) -> str:
        return "dict"

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

    def _setitem_replace(self, key: str, value: Any):
        """
        Set a key by completely replacing the old child with a new one
        """

        # remove the old child if any
        if key in self._children:
            self.remove_child(key)

        # use the generic pack method to add the new child
        self.pack(key, value)

    def _setitem_sparse(self, key: str, value: Any):
        """
        Set a key by updating its descendants individually. This only works if both the old and new values are dict nodes
        """

        old_child = self._children[key]

        # check which subkeys need to be added, updated or removed and perform the necessary operations
        old_keys = set(old_child.keys())
        new_keys = set(value.keys())

        # remove keys that are not in the new value
        for key in old_keys - new_keys:
            old_child.remove_child(key)

        # update keys that are in both the old and new values
        for key in old_keys & new_keys:
            old_child[key] = value[key]

        # add keys that are not in the old value
        for key in new_keys - old_keys:
            old_child.pack(key, value[key])

    def _can_use_setitem_sparse(self, key: str, value: Any) -> bool:
        # child must exist
        if key not in self._children:
            return False

        # child must be a dict node
        if not isinstance(self._children[key], ReactiveDictNode):
            return False

        # value must be a dict
        if not isinstance(value, dict):
            return False

        # check if there are any keys that need to be updated, e.g. that exist in both the old and new values
        if set(self._children[key].keys()) & set(value.keys()):
            return True

        # if there are only keys to be added or removed, a sparse update does not make sense
        return False

    def __setitem__(self, key: str, value: Any):
        if "." in key:
            self._invoke_nested_key_method(key, ReactiveDictNode.__setitem__, value)
            return

        old_child = self._children.get(key)

        # if the old child is a leaf node and the new value is an atomic type, update the value directly
        if old_child and old_child.is_leaf() and isinstance(value, AtomicType):
            old_child.set_value(value)
            return

        # use either the replace or update method to set the 
        if self._can_use_setitem_sparse(key, value):
            self._setitem_sparse(key, value)
        else:
            self._setitem_replace(key, value)

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

    def __len__(self) -> int:
        return len(self._children)

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
        key = next(reversed(self._children))
        value = self.pop(key)
        return key, value

    def setdefault(self, key: str, default: Any = None) -> UnpackedType:
        if key not in self:
            self[key] = default

        return self[key]

    def json(self) -> dict:
        return {key: child.json() for key, child in self._children.items()}

    def __str__(self) -> str:
        return f"ReactiveDictNode({{ {', '.join(f'{key}: {child}' for key, child in self._children.items())} }})"

    def unpack(self) -> "ReactiveDictNode":
        return self

    def pack_dict(self, key: str, data: dict):
        child = ReactiveDictNode(key)
        self.add_child(child)

        # invoke the generic pack method for each key-value pair
        for k, v in data.items():
            child.pack(k, v)


ReactiveNode.PACK_METHODS[dict] = ReactiveDictNode.pack_dict
