import pytest
from perci import reactive
from perci.node import ReactiveNode
from perci.list_node import ReactiveListNode


def test_getitem():
    state = reactive(
        {
            "test": [42, 43],
        }
    )

    x = state["test"][0]

    assert x == 42


def test_setitem():
    state = reactive(
        {
            "test": [42, 43],
        }
    )

    state["test"][0] = 44

    assert state["test"][0] == 44
    assert state["test"][-1] == 43

    # setitem on unknown key
    with pytest.raises(IndexError):
        state["test"][2] = 45


def test_delitem():
    state = reactive(
        {
            "test": [42, 43],
        }
    )

    del state["test"][0]

    assert list(state["test"].get_children()) == ["0"]

    assert state["test"][0] == 43
    assert len(state["test"]) == 1

    # delitem on unknown key
    with pytest.raises(IndexError):
        del state["test"][1]

    with pytest.raises(IndexError):
        del state["test"][-2]

    # delete remaining item
    del state["test"][-1]

    assert len(state["test"]) == 0
