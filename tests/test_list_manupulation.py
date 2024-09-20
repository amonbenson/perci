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

    assert len(state["test"]) == 1
    assert state["test"][0] == 43

    # delitem on unknown key
    with pytest.raises(IndexError):
        del state["test"][1]

    with pytest.raises(IndexError):
        del state["test"][-2]

    # delete remaining item
    del state["test"][-1]

    assert len(state["test"]) == 0


def test_append():
    state = reactive(
        {
            "test": [42],
        }
    )

    state["test"].append(43)

    assert len(state["test"]) == 2
    assert state["test"][1] == 43


def test_insert():
    state = reactive(
        {
            "test": [42, 44],
        }
    )

    state["test"].insert(1, 43)

    assert len(state["test"]) == 3
    assert state["test"][1] == 43
    assert state["test"][2] == 44

    # insert at index 0
    state["test"].insert(0, 41)

    assert len(state["test"]) == 4
    assert state["test"][0] == 41
    assert state["test"][1] == 42
    assert state["test"][2] == 43
    assert state["test"][3] == 44
