# pylint: skip-file

from src.perci import create_root_node
from src.perci.node import ReactiveNode
from src.perci.namespace import ReactiveNamespace


def test_empty_node():
    node = create_root_node()

    assert isinstance(node.get_namespace(), ReactiveNamespace)

    assert node.get_key() == "root"
    assert node.get_parent() is None
    assert node.get_path() == ["root"]
    assert node.is_leaf()
    assert node.is_root()


def test_add_single_child():
    parent = create_root_node("parent")

    child = ReactiveNode("child")
    parent.add_child(child)

    assert child.get_key() == "child"
    assert child.get_parent() == parent
    assert child.get_path() == ["parent", "child"]
    assert child.is_leaf()
    assert not child.is_root()

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.get_child("child") == child
    assert not parent.is_leaf()
    assert parent.is_root()

    assert isinstance(parent.get_namespace(), ReactiveNamespace)
    assert parent.get_namespace() == child.get_namespace()


def test_add_multiple_children():
    parent = create_root_node("parent")

    child1 = ReactiveNode("child1")
    parent.add_child(child1)

    child2 = ReactiveNode("child2")
    parent.add_child(child2)

    assert child1.get_key() == "child1"
    assert child1.get_parent() == parent
    assert child1.get_path() == ["parent", "child1"]
    assert child1.is_leaf()
    assert not child1.is_root()

    assert child2.get_key() == "child2"
    assert child2.get_parent() == parent
    assert child2.get_path() == ["parent", "child2"]
    assert child2.is_leaf()
    assert not child2.is_root()

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.get_child("child1") == child1
    assert parent.get_child("child2") == child2
    assert not parent.is_leaf()
    assert parent.is_root()

    assert isinstance(parent.get_namespace(), ReactiveNamespace)
    assert parent.get_namespace() == child1.get_namespace() == child2.get_namespace()


def test_add_nested_children():
    parent = create_root_node("parent")

    child1 = ReactiveNode("child1")
    parent.add_child(child1)

    child2 = ReactiveNode("child2")
    child1.add_child(child2)

    assert child1.get_key() == "child1"
    assert child1.get_parent() == parent
    assert child1.get_path() == ["parent", "child1"]
    assert not child1.is_leaf()
    assert not child1.is_root()

    assert child2.get_key() == "child2"
    assert child2.get_parent() == child1
    assert child2.get_path() == ["parent", "child1", "child2"]
    assert child2.is_leaf()
    assert not child2.is_root()

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.get_child("child1") == child1
    assert parent.get_child("child1").get_child("child2") == child2
    assert not parent.is_leaf()
    assert parent.is_root()

    assert isinstance(parent.get_namespace(), ReactiveNamespace)
    assert parent.get_namespace() == child1.get_namespace() == child2.get_namespace()


def test_remove_child():
    parent = create_root_node("parent")

    child = ReactiveNode("child")
    parent.add_child(child)

    parent.remove_child("child")

    assert parent.get_child("child") is None
    assert child.get_parent() is None
    assert child.get_path() == ["child"]
    assert child.is_leaf()
    assert child.is_root()

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.is_leaf()
    assert parent.is_root()

    assert isinstance(parent.get_namespace(), ReactiveNamespace)
    assert child.get_namespace() is None


def test_remove_nested_children():
    parent = create_root_node("parent")

    child1 = ReactiveNode("child1")
    parent.add_child(child1)

    child2 = ReactiveNode("child2")
    child1.add_child(child2)

    parent.remove_child("child1")

    assert parent.get_child("child1") is None
    assert child1.get_parent() is None
    assert child1.get_path() == ["child1"]
    assert not child1.is_leaf()
    assert child1.is_root()

    assert child1.get_child("child2") is child2
    assert child2.get_parent() == child1
    assert child2.get_path() == ["child1", "child2"]
    assert child2.is_leaf()
    assert not child2.is_root()

    assert parent.get_key() == "parent"
    assert parent.get_parent() is None
    assert parent.get_path() == ["parent"]
    assert parent.is_leaf()
    assert parent.is_root()

    assert isinstance(parent.get_namespace(), ReactiveNamespace)
    assert child1.get_namespace() is None
    assert child2.get_namespace() is None
