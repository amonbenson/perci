# pylint: skip-file

from unittest.mock import Mock, call
from src.perci import reactive, watch
from src.perci.changes import Change, AddChange, RemoveChange, UpdateChange


def test_add_keys():
    state = reactive(
        {
            "name": "Alice",
            "age": 25,
        }
    )

    handler = Mock()
    watch(state, handler)

    state["name"] = "Bob"
    handler.assert_called_once_with(UpdateChange(path=["root", "name"], value="Bob"))
    handler.reset_mock()

    state["address"] = {
        "city": "New York",
        "state": "NY",
    }
    handler.assert_has_calls(
        [
            call(AddChange(path=["root"], key="address")),
            call(AddChange(path=["root", "address"], key="city")),
            call(UpdateChange(path=["root", "address", "city"], value="New York")),
            call(AddChange(path=["root", "address"], key="state")),
            call(UpdateChange(path=["root", "address", "state"], value="NY")),
        ]
    )
    handler.reset_mock()


def test_update_keys():
    state = reactive(
        {
            "name": "Alice",
            "age": 25,
        }
    )

    handler = Mock()
    watch(state, handler)

    state["age"] = {
        "years": 25,
        "months": 6,
    }
    handler.assert_has_calls(
        [
            call(RemoveChange(path=["root"], key="age")),
            call(AddChange(path=["root"], key="age")),
            call(AddChange(path=["root", "age"], key="years")),
            call(UpdateChange(path=["root", "age", "years"], value=25)),
            call(AddChange(path=["root", "age"], key="months")),
            call(UpdateChange(path=["root", "age", "months"], value=6)),
        ]
    )
    handler.reset_mock()

    state["age"] = 26
    handler.assert_has_calls(
        [
            call(RemoveChange(path=["root"], key="age")),
            call(AddChange(path=["root"], key="age")),
            call(UpdateChange(path=["root", "age"], value=26)),
        ]
    )
    handler.reset_mock()
