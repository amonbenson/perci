# pylint: skip-file

from src.perci.core.node import Node, RootNode


def test_remove_pathological():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    s.add_child(t)

    s.remove_child("t")

    # check if tree is built correctly
    assert r._children == {"s": s}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent is None
    assert t._root is None
    assert t._path == ["t"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "s", "t"], "type": "add"}, {"path": ["r", "s", "t"], "type": "remove"}]


def test_remove_pathological_reverse():
    r = RootNode("r")
    s = Node("s")
    t = Node("t")

    s.add_child(t)
    r.add_child(s)

    r.remove_child("s")

    # check if tree is built correctly
    assert r._children == {}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {"t": t}
    assert s._parent is None
    assert s._root is None
    assert s._path == ["s"]

    assert t._children == {}
    assert t._parent == s
    assert t._root is None
    assert t._path == ["s", "t"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "s"], "type": "remove"}]


def test_remove_flat():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    r.add_child(t)

    u = Node("u")
    r.add_child(u)

    r.remove_child("t")

    # check if tree is built correctly
    assert r._children == {"s": s, "u": u}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent is None
    assert t._root is None
    assert t._path == ["t"]

    assert u._children == {}
    assert u._parent == r
    assert u._root == r
    assert u._path == ["r", "u"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "t"], "type": "add"}, {"path": ["r", "u"], "type": "add"}, {"path": ["r", "t"], "type": "remove"}]


def test_remove_complex():
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

    r.remove_child("v")
    s.remove_child("t")

    # check if tree is built correctly
    assert r._children == {"s": s}
    assert r._parent is None
    assert r._root == r
    assert r._path == ["r"]

    assert s._children == {"u": u}
    assert s._parent == r
    assert s._root == r
    assert s._path == ["r", "s"]

    assert t._children == {}
    assert t._parent is None
    assert t._root is None
    assert t._path == ["t"]

    assert u._children == {}
    assert u._parent == s
    assert u._root == r
    assert u._path == ["r", "s", "u"]

    assert v._children == {"w": w}
    assert v._parent is None
    assert v._root is None
    assert v._path == ["v"]

    assert w._children == {}
    assert w._parent == v
    assert w._root is None
    assert w._path == ["v", "w"]

    # check if changes are tracked correctly
    assert r._change_tracker.get_changes() == [
        {"path": ["r", "s"], "type": "add"},
        {"path": ["r", "s", "t"], "type": "add"},
        {"path": ["r", "s", "u"], "type": "add"},
        {"path": ["r", "v"], "type": "add"},
        {"path": ["r", "v", "w"], "type": "add"},
        {"path": ["r", "v"], "type": "remove"},
        {"path": ["r", "s", "t"], "type": "remove"},
    ]
