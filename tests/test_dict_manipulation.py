# pylint: skip-file

from src.perci import create_dict_node
from src.perci.dict_node import ReactiveDictNode


def test_add_atomic_child():
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


def test_add_dict_child():
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
