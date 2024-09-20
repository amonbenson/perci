# pylint: skip-file

import time
from unittest.mock import Mock, call
from perci import reactive, watch, create_queue_watcher
from perci.changes import AddChange, RemoveChange, UpdateChange


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
            call(AddChange(path=["root"], key="address", repr="dict", value=None)),
            call(AddChange(path=["root", "address"], key="city", repr="value", value="New York")),
            call(AddChange(path=["root", "address"], key="state", repr="value", value="NY")),
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
            call(AddChange(path=["root"], key="age", repr="dict", value=None)),
            call(AddChange(path=["root", "age"], key="years", repr="value", value=25)),
            call(AddChange(path=["root", "age"], key="months", repr="value", value=6)),
        ]
    )
    handler.reset_mock()

    state["age"] = 26
    handler.assert_has_calls(
        [
            call(RemoveChange(path=["root"], key="age")),
            call(AddChange(path=["root"], key="age", repr="value", value=26)),
        ]
    )
    handler.reset_mock()


def test_remove_keys():
    state = reactive(
        {
            "name": "Alice",
            "age": 25,
        }
    )

    handler = Mock()
    watch(state, handler)

    del state["age"]
    handler.assert_called_once_with(RemoveChange(path=["root"], key="age"))
    handler.reset_mock()

    del state["name"]
    handler.assert_called_once_with(RemoveChange(path=["root"], key="name"))
    handler.reset_mock()


def test_watcher_remove():
    state = reactive(
        {
            "name": {
                "first": "Alice",
                "last": "Smith",
            },
            "age": 25,
        }
    )

    first_handler = Mock()
    name_handler = Mock()
    root_handler = Mock()

    # setup watchers
    watch(state["name"].get_child("first"), first_handler)
    watch(state["name"], name_handler)
    watch(state, root_handler)

    # update age. This should trigger only the root handler
    state["age"] = 26

    first_handler.assert_not_called()
    name_handler.assert_not_called()
    root_handler.assert_called_once_with(UpdateChange(path=["root", "age"], value=26))

    root_handler.reset_mock()

    # update first name. This should trigger all the handlers
    state["name"]["first"] = "Bob"

    first_handler.assert_called_once_with(UpdateChange(path=["root", "name", "first"], value="Bob"))
    name_handler.assert_called_once_with(UpdateChange(path=["root", "name", "first"], value="Bob"))
    root_handler.assert_called_once_with(UpdateChange(path=["root", "name", "first"], value="Bob"))

    first_handler.reset_mock()
    name_handler.reset_mock()
    root_handler.reset_mock()

    # remove name. This should only trigger the root handler, as the other handlers are now invalid
    del state["name"]

    first_handler.assert_not_called()
    name_handler.assert_not_called()
    root_handler.assert_called_once_with(RemoveChange(path=["root"], key="name"))

    # make sure that only the root handler remains
    assert len(state.get_namespace().get_watchers()) == 1
    assert state.get_namespace().get_watchers()[0].handler == root_handler


def test_update_sparse_keys():
    state = reactive(
        {
            "name": {
                "first": "Alice",
                "last": "Smith",
            },
            "age": 25,
        },
    )

    handler = Mock()
    watch(state, handler)

    state["name"] = {
        "first": "Bob",
        "last": "Johnson",
    }

    handler.assert_has_calls(
        [
            call(UpdateChange(path=["root", "name", "first"], value="Bob")),
            call(UpdateChange(path=["root", "name", "last"], value="Johnson")),
        ],
        any_order=True,
    )


def test_queue_watcher():
    state = reactive(
        {
            "name": {
                "first": "Alice",
                "last": "Smith",
            },
            "age": 25,
        }
    )

    watcher = create_queue_watcher(state)

    # force a replace update
    state["name"] = {}
    state["name"]["first"] = "Bob"
    state["name"]["last"] = "Johnson"

    changes = watcher.get_changes()

    assert changes == [
        RemoveChange(path=["root"], key="name"),
        AddChange(path=["root"], key="name", repr="dict", value=None),
        AddChange(path=["root", "name"], key="first", repr="value", value="Bob"),
        AddChange(path=["root", "name"], key="last", repr="value", value="Johnson"),
    ]

    # force a sparse update
    state["name"] = {
        "first": "Alice",
        "last": "Smith",
    }

    changes = watcher.get_changes()

    assert len(changes) == 2
    assert UpdateChange(path=["root", "name", "first"], value="Alice") in changes
    assert UpdateChange(path=["root", "name", "last"], value="Smith") in changes
