from typing import Any
from perci import reactive
from perci.node import ReactiveNode
from perci.dict_node import ReactiveDictNode
from perci.list_node import ReactiveListNode


def test_pack_simple():
    state = reactive({"test": [42, 43]})

    test_node = state.get_child("test")
    assert isinstance(test_node, ReactiveListNode)

    assert isinstance(test_node.get_child("0"), ReactiveNode)
    assert test_node.get_child("0").get_value() == 42

    assert isinstance(test_node.get_child("1"), ReactiveNode)
    assert test_node.get_child("1").get_value() == 43


def test_unpack_simple():
    state = reactive({"test": [42, 43]})

    x = state["test"]

    assert len(state["test"]) == 2
    assert x[0] == 42
    assert x[1] == 43
