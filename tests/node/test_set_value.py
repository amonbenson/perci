# pylint: skip-file

from src.perci.core.node import Node, RootNode


def test_set_value():
    r = RootNode("r")

    s = Node("s")
    r.add_child(s)

    t = Node("t")
    s.add_child(t)

    s.set_value(1)
    t.set_value(2)

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
    assert r._change_tracker.get_changes() == [{"path": ["r", "s"], "type": "add"}, {"path": ["r", "s", "t"], "type": "add"}, {"path": ["r", "s"], "type": "update", "value": 1}, {"path": ["r", "s", "t"], "type": "update", "value": 2}]
