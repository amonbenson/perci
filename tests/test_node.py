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


def test_single_child():
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
