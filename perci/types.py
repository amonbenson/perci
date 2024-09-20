from typing import Union


AtomicType = int | float | str | bool | None
UnpackedType = Union[AtomicType, dict, list]
