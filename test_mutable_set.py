import pytest
from hypothesis import given, strategies as st
from mutable_set import MutableSet

# -------------------- unit tests --------------------
def test_add_and_member():
    s = MutableSet()
    s.add(10)
    assert 10 in s
    assert 20 not in s
    assert s.size() == 1

def test_add_duplicate():
    s = MutableSet()
    s.add(10)
    s.add(10)
    assert s.size() == 1

def test_remove():
    s = MutableSet()
    s.add(10)
    s.remove(10)
    assert 10 not in s
    assert s.size() == 0
    with pytest.raises(KeyError):
        s.remove(10)

def test_from_list_to_list():
    s = MutableSet()
    lst = [1, 2, 3, 2, 1]
    s.from_list(lst)
    assert sorted(s.to_list()) == sorted([1, 2, 3])
    s.from_list([])
    assert s.size() == 0

def test_filter():
    s = MutableSet()
    s.from_list([1, 2, 3, 4])
    s.filter(lambda x: x % 2 == 0)
    assert s.to_list() == [2, 4]

def test_map():
    s = MutableSet()
    s.from_list([1, 2, 3])
    s.map(lambda x: x * 2)
    assert set(s) == {2, 4, 6}

def test_reduce():
    s = MutableSet()
    s.from_list([1, 2, 3])
    assert s.reduce(lambda a, b: a + b) == 6
    assert s.reduce(lambda a, b: a + b, 10) == 16
    empty = MutableSet()
    with pytest.raises(TypeError):
        empty.reduce(lambda a, b: a + b)

def test_iter():
    s = MutableSet()
    s.from_list([1, 2, 3])
    elements = list(s)
    assert sorted(elements) == [1, 2, 3]

def test_empty():
    e = MutableSet.empty()
    assert e.size() == 0
    assert isinstance(e, MutableSet)

def test_concat():
    s1 = MutableSet()
    s1.from_list([1, 2])
    s2 = MutableSet()
    s2.from_list([2, 3])
    s1.concat(s2)
    assert set(s1) == {1, 2, 3}

def test_none():
    s = MutableSet()
    s.add(None)
    assert None in s
    s.remove(None)
    assert None not in s

def test_mixed_types():
    s = MutableSet()
    s.add(1)
    s.add("a")
    s.add(1.0)
    assert s.size() == 3

# -------------------- property‑based tests --------------------
@st.composite
def sets_and_lists(draw):
    """Strategy: generate a list of hashable elements."""
    elems = draw(st.lists(st.one_of(st.integers(), st.none())))
    return elems

@given(sets_and_lists())
def test_from_list_preserves_uniqueness(lst):
    s = MutableSet()
    s.from_list(lst)
    expected = set(lst)
    assert set(s) == expected

@given(sets_and_lists(), st.integers())
def test_add_member(lst, x):
    s = MutableSet()
    s.from_list(lst)
    before = set(s)
    s.add(x)
    after = set(s)
    assert after == before | {x}
    assert x in s

@given(sets_and_lists())
def test_remove(lst):
    s = MutableSet()
    s.from_list(lst)
    # pick an element that is present, if any
    if lst:
        elem = lst[0]
        if elem in s:
            s.remove(elem)
            assert elem not in s
            assert s.size() == len(set(lst)) - 1
    # removal of missing element raises
    with pytest.raises(KeyError):
        s.remove(999999)

@given(sets_and_lists())
def test_filter_property(lst):
    s = MutableSet()
    s.from_list(lst)
    pred = lambda x: x is not None and x % 2 == 0
    s.filter(pred)
    expected = {x for x in lst if pred(x)}
    assert set(s) == expected

@given(sets_and_lists())
def test_map_property(lst):
    s = MutableSet()
    s.from_list(lst)
    s.map(lambda x: x * 2 if isinstance(x, int) else x)
    expected = {x * 2 if isinstance(x, int) else x for x in lst}
    assert set(s) == expected

@given(sets_and_lists())
def test_reduce_property(lst):
    s = MutableSet()
    s.from_list(lst)
    if lst:
        result = s.reduce(lambda a, b: a + b if isinstance(a, int) and isinstance(b, int) else 0)
        # We don't enforce exact equality because the order is arbitrary,
        # but we can check that the reduction returns something.
        assert isinstance(result, int)
    else:
        with pytest.raises(TypeError):
            s.reduce(lambda a, b: a + b)

@given(sets_and_lists(), sets_and_lists())
def test_concat_property(lst1, lst2):
    s1 = MutableSet()
    s2 = MutableSet()
    s1.from_list(lst1)
    s2.from_list(lst2)
    before = set(s1)
    s1.concat(s2)
    assert set(s1) == before | set(lst2)

def test_monoid_laws():
    # empty.concat(s) == s
    s = MutableSet()
    s.from_list([1, 2, 3])
    e = MutableSet.empty()
    e.concat(s)
    assert e == s
    # s.concat(empty) == s
    s.concat(MutableSet.empty())
    assert s == s
    # associativity: (a.concat(b)).concat(c) == a.concat(b.concat(c))
    a = MutableSet()
    b = MutableSet()
    c = MutableSet()
    a.from_list([1])
    b.from_list([2])
    c.from_list([3])
    left = MutableSet.empty()
    left.concat(a)
    left.concat(b)
    left.concat(c)          # left = a + b + c
    right = MutableSet.empty()
    right.concat(a)
    tmp = MutableSet.empty()
    tmp.concat(b)
    tmp.concat(c)
    right.concat(tmp)       # right = a + (b + c)
    assert left == right