from .core.node import RootNode
from .core.event import EventEmitter


class AsyncNode(RootNode, EventEmitter):
    def __init__(self, root_key: str):
        RootNode.__init__(self, root_key)
        EventEmitter.__init__(self)
