# pylint: skip-file

from perci import create_dict_node
from perci.dict_node import ReactiveDictNode


def test_empty_node():
    node = create_dict_node()

    assert node.get_namespace() is not None

    assert node.get_key() == "root"
    assert node.get_parent() is None
    assert node.get_path() == ["root"]
    assert node.is_leaf()
    assert node.is_root()


def test_add_single_child():
    parent = create_dict_node(
        {
            "child": 42,
        },
        "parent",
    )

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child")

    child = parent.get_child("child")

    assert child.get_key() == "child"
    assert child.get_parent() == parent
    assert child.get_path() == ["parent", "child"]
    assert child.is_leaf()
    assert not child.is_root()
    assert child.get_value() == 42

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.is_root()
    assert not parent.is_leaf()


def test_add_multiple_children():
    parent = create_dict_node(
        {
            "child1": 42,
            "child2": 43,
        },
        "parent",
    )

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child1")
    assert parent.has_child("child2")

    child1 = parent.get_child("child1")

    assert child1.get_key() == "child1"
    assert child1.get_parent() == parent
    assert child1.get_path() == ["parent", "child1"]
    assert child1.is_leaf()
    assert not child1.is_root()
    assert child1.get_value() == 42

    child2 = parent.get_child("child2")

    assert child2.get_key() == "child2"
    assert child2.get_parent() == parent
    assert child2.get_path() == ["parent", "child2"]
    assert child2.is_leaf()
    assert not child2.is_root()
    assert child2.get_value() == 43


def test_add_nested_children():
    parent = create_dict_node(
        {
            "child": {
                "nested_child": 42,
            }
        },
        "parent",
    )

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child")

    child = parent.get_child("child")

    assert len(child.get_children()) == 1
    assert child.get_key() == "child"
    assert child.get_parent() == parent
    assert child.get_path() == ["parent", "child"]
    assert not child.is_leaf()
    assert not child.is_root()

    assert child.has_child("nested_child")

    nested_child = child.get_child("nested_child")

    assert nested_child.get_key() == "nested_child"
    assert nested_child.get_parent() == child
    assert nested_child.get_path() == ["parent", "child", "nested_child"]
    assert nested_child.is_leaf()
    assert not nested_child.is_root()
    assert nested_child.get_value() == 42


def test_add_multiple_nested_children():
    parent = create_dict_node(
        {
            "child1": {
                "nested_child1": 42,
            },
            "child2": {
                "nested_child2": 43,
            },
        },
        "parent",
    )

    assert isinstance(parent, ReactiveDictNode)
    assert parent.has_child("child1")
    assert parent.has_child("child2")

    child1 = parent.get_child("child1")

    assert len(child1.get_children()) == 1
    assert child1.get_key() == "child1"
    assert child1.get_parent() == parent
    assert child1.get_path() == ["parent", "child1"]
    assert not child1.is_leaf()
    assert not child1.is_root()

    assert child1.has_child("nested_child1")

    nested_child1 = child1.get_child("nested_child1")

    assert nested_child1.get_key() == "nested_child1"
    assert nested_child1.get_parent() == child1
    assert nested_child1.get_path() == ["parent", "child1", "nested_child1"]
    assert nested_child1.is_leaf()
    assert not nested_child1.is_root()
    assert nested_child1.get_value() == 42

    child2 = parent.get_child("child2")

    assert len(child2.get_children()) == 1
    assert child2.get_key() == "child2"
    assert child2.get_parent() == parent
    assert child2.get_path() == ["parent", "child2"]
    assert not child2.is_leaf()
    assert not child2.is_root()

    assert child2.has_child("nested_child2")

    nested_child2 = child2.get_child("nested_child2")

    assert nested_child2.get_key() == "nested_child2"
    assert nested_child2.get_parent() == child2
    assert nested_child2.get_path() == ["parent", "child2", "nested_child2"]
    assert nested_child2.is_leaf()
    assert not nested_child2.is_root()
    assert nested_child2.get_value() == 43
