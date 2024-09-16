# pylint: skip-file

from unittest.mock import Mock, call
from src.perci import reactive, watch
from src.perci.changes import Change, AddChange, RemoveChange, UpdateChange


def test_root_watcher():
    state = reactive(
        {
            "name": "Alice",
            "age": 25,
        }
    )

    handler = Mock()

    watcher = watch(state, handler)

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
