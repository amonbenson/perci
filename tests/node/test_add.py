# pylint: skip-file

import pytest
from src.core.node import Node, RootNode


def test_add_pathological():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    s.add_child(t)

    # check if tree is built correctly
    assert r._children == {"s": s}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {"t": t}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent == s
    assert t._root == r
    assert t._path == ["r", "s", "t"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "s", "t"], "type": "add"}]


def test_add_pathological_reverse():
    r = RootNode("r")
    s = Node("s")
    t = Node("t")

    s.add_child(t)
    r.add_child(s)

    # check if tree is built correctly
    assert r._children == {"s": s}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {"t": t}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent == s
    assert t._root == r
    assert t._path == ["r", "s", "t"]

    # check if changes are tracked correctly
    # note that the s -> t change is not tracked because s was not a child of r when t was added
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}]


def test_add_flat():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    r.add_child(t)

    u = Node("u")
    r.add_child(u)

    # check if tree is built correctly
    assert r._children == {"s": s, "t": t, "u": u}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent == r
    assert t._root == r
    assert t._path == ["r", "t"]

    assert u._children == {}
    assert u._parent == r
    assert u._root == r
    assert u._path == ["r", "u"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "t"], "type": "add"}, {"path": ["r", "u"], "type": "add"}]


def test_add_complex():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    s.add_child(t)

    u = Node("u")
    s.add_child(u)

    v = Node("v")
    r.add_child(v)

    w = Node("w")
    v.add_child(w)

    # check if tree is built correctly
    assert r._children == {"s": s, "v": v}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {"t": t, "u": u}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent == s
    assert t._root == r
    assert t._path == ["r", "s", "t"]

    assert u._children == {}
    assert u._parent == s
    assert u._root == r
    assert u._path == ["r", "s", "u"]

    assert v._children == {"w": w}
    assert v._parent == r
    assert v._root == r
    assert v._path == ["r", "v"]

    assert w._children == {}
    assert w._parent == v
    assert w._root == r
    assert w._path == ["r", "v", "w"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [
        {"path": ["r", "s"], "type": "add"},
        {"path": ["r", "s", "t"], "type": "add"},
        {"path": ["r", "s", "u"], "type": "add"},
        {"path": ["r", "v"], "type": "add"},
        {"path": ["r", "v", "w"], "type": "add"},
    ]


def test_invalid_key():
    Node("abc")
    Node("a_b")
    Node("a-b")
    Node("a1")
    Node("1a")

    with pytest.raises(ValueError):
        Node("a b")

    with pytest.raises(ValueError):
        Node("a.b")

    with pytest.raises(ValueError):
        Node("a/b")

    with pytest.raises(ValueError):
        Node("")
