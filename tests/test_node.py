# pylint: skip-file

from src.perci import reactive
from src.perci.namespace import ReactiveNamespace


def test_empty_reactive_node():
    node = reactive()

    assert isinstance(node.get_namespace(), ReactiveNamespace)

    assert node.get_key() == "root"
    assert node.get_absolute_key() == "root"
    assert node.get_parent() is None
    assert node.get_path() == []
    assert node.is_leaf()
    assert node.is_root()
