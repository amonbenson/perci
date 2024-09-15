# pylint: skip-file

import pytest
from src.core.node import Node, RootNode


class SomeClass:
    """
    Dummy class to test unsupported types
    """


def test_dict_conversion():
    data = {"s": {"t": 1, "u": 2}, "v": {"w": 3}}

    r = RootNode.from_dict(data, "r")

    # check if tree is built correctly
    assert list(r.get_children().keys()) == ["s", "v"]
    assert r.get_parent() is None
    assert r.get_root() == r
    assert r.get_path() == ["r"]

    s = r.get_child("s")
    assert list(s.get_children().keys()) == ["t", "u"]
    assert s.get_parent() == r
    assert s.get_root() == r
    assert s.get_path() == ["r", "s"]

    t = s.get_child("t")
    assert list(t.get_children()) == []
    assert t.get_parent() == s
    assert t.get_root() == r
    assert t.get_path() == ["r", "s", "t"]

    u = s.get_child("u")
    assert list(u.get_children()) == []
    assert u.get_parent() == s
    assert u.get_root() == r
    assert u.get_path() == ["r", "s", "u"]

    v = r.get_child("v")
    assert list(v.get_children().keys()) == ["w"]
    assert v.get_parent() == r
    assert v.get_root() == r
    assert v.get_path() == ["r", "v"]

    w = v.get_child("w")
    assert list(w.get_children().keys()) == []
    assert w.get_parent() == v
    assert w.get_root() == r
    assert w.get_path() == ["r", "v", "w"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [
        {"path": ["r", "s"], "type": "add"},
        {"path": ["r", "s", "t"], "type": "add"},
        {"path": ["r", "s", "t"], "type": "update", "value": 1},
        {"path": ["r", "s", "u"], "type": "add"},
        {"path": ["r", "s", "u"], "type": "update", "value": 2},
        {"path": ["r", "v"], "type": "add"},
        {"path": ["r", "v", "w"], "type": "add"},
        {"path": ["r", "v", "w"], "type": "update", "value": 3},
    ]

    # check if dict conversion works correctly
    assert r.as_dict() == data


def test_get_item():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")

    assert type(node["s"]) == Node
    assert node["s"]["t"] == 1

    with pytest.raises(KeyError):
        node["x"]


def test_get_item_path():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")

    assert node["s.t"] == 1

    with pytest.raises(KeyError):
        node["s.x"]

    with pytest.raises(KeyError):
        node["x.t"]


def test_set_item_atomic():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")
    node.get_change_tracker().clear()

    node["s"]["t"] = 4
    assert node["s"]["t"] == 4
    assert node.get_change_tracker().get_changes() == [{"path": ["r", "s", "t"], "type": "update", "value": 4}]
    node.get_change_tracker().clear()

    # overwrite non-leaf node with a leaf node
    node["s"] = 5
    assert type(node.get_child("s")) == Node
    assert node.get_child("s").is_leaf()
    assert node["s"] == 5
    assert node.get_change_tracker().get_changes() == [{"path": ["r", "s"], "type": "remove"}, {"path": ["r", "s"], "type": "add"}, {"path": ["r", "s"], "type": "update", "value": 5}]


def test_set_item_dict():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")
    node.get_change_tracker().clear()

    # overwrite leaf node with a dict
    node["s"] = {"x": 8, "y": 9}

    assert node.as_dict() == {"s": {"x": 8, "y": 9}, "v": {"w": 3}}
    assert node.get_change_tracker().get_changes() == [
        {"path": ["r", "s"], "type": "remove"},
        {"path": ["r", "s"], "type": "add"},
        {"path": ["r", "s", "x"], "type": "add"},
        {"path": ["r", "s", "x"], "type": "update", "value": 8},
        {"path": ["r", "s", "y"], "type": "add"},
        {"path": ["r", "s", "y"], "type": "update", "value": 9},
    ]


def test_set_item_unsupported_type():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")

    # direct node assignment is not allowed via the dict interface
    with pytest.raises(ValueError):
        node["s"] = Node("xyz")

    # unknown type assignment is not allowed
    with pytest.raises(ValueError):
        node["s"] = SomeClass()


def test_set_item_path():
    node = RootNode.from_dict({"s": {"t": 1, "u": 2}, "v": {"w": 3}}, "r")
    node.get_change_tracker().clear()

    node["s.t"] = 4
    assert node["s"]["t"] == 4

    node["s.x"] = 5
    assert node["s"]["x"] == 5

    with pytest.raises(KeyError):
        node["x.t"] = 6
