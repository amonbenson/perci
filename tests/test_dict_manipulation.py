# pylint: skip-file

from src.perci import create_dict_node
from src.perci.dict_node import ReactiveDictNode


def test_add_atomic():
    parent = create_dict_node({}, "parent")

    parent["child"] = 42

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child")

    child = parent.get_child("child")

    assert child.get_key() == "child"
    assert child.get_parent() == parent
    assert child.get_path() == ["parent", "child"]
    assert child.is_leaf()
    assert not child.is_root()
    assert child.get_value() == 42


def test_add_dict():
    parent = create_dict_node({}, "parent")

    parent["child"] = {
        "grandchild": 42,
    }

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child")

    child = parent.get_child("child")

    assert child.get_key() == "child"
    assert child.get_parent() == parent
    assert child.get_path() == ["parent", "child"]
    assert not child.is_leaf()
    assert not child.is_root()

    assert child.has_child("grandchild")

    grandchild = child.get_child("grandchild")

    assert grandchild.get_key() == "grandchild"
    assert grandchild.get_parent() == child
    assert grandchild.get_path() == ["parent", "child", "grandchild"]
    assert grandchild.is_leaf()
    assert not grandchild.is_root()
    assert grandchild.get_value() == 42

    # changing the value should not add a new child but update the existing one
    parent["child"]["grandchild"] = 43

    assert grandchild.get_value() == 43

    # adding a dict should replace the old grandchild
    parent["child"]["grandchild"] = {
        "great_grandchild": 44,
    }

    assert grandchild != child.get_child("grandchild")
    assert child["grandchild"]["great_grandchild"] == 44


def test_delete():
    parent = create_dict_node(
        {
            "child": {
                "grandchild": 42,
            },
        },
        "parent",
    )

    assert parent.has_child("child")

    del parent["child"]

    assert not parent.has_child("child")
    assert parent.is_leaf()
    assert parent.is_root()


def test_get():
    parent = create_dict_node(
        {
            "child": {
                "grandchild": 42,
            },
        },
        "parent",
    )

    assert parent.get("child").get("grandchild") == 42
    assert parent.get("child").get("grandchild2", 43) == 43


def test_keys():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.keys() == ["child1", "child2"]


def test_values():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.values() == [42, 43]


def test_items():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.items() == [("child1", 42), ("child2", 43)]


def test_clear():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    parent.clear()

    assert parent.is_leaf()
    assert parent.is_root()
    assert parent.items() == []


def test_update():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    parent.update(
        {
            "child2": 44,
            "child3": 45,
        }
    )

    assert parent.items() == [("child1", 42), ("child2", 44), ("child3", 45)]


def test_pop():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.pop("child1") == 42
    assert parent.pop("child3", 45) == 45
    assert parent.items() == [("child2", 43)]


def test_popitem():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.popitem() == ("child2", 43)
    assert parent.items() == [("child1", 42)]


def test_setdefault():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert parent.setdefault("child1", 44) == 42
    assert parent.setdefault("child3", 45) == 45
    assert parent.items() == [("child1", 42), ("child2", 43), ("child3", 45)]
