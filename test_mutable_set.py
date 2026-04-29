import pytest
from hypothesis import given, strategies as st

from mutable_set import MutableSet


def test_add_member_size():
    s = MutableSet()
    s.add(1)
    s.add(1)
    assert s.member(1)
    assert 1 in s
    assert s.size() == 1


def test_remove():
    s = MutableSet()
    s.add(10)
    s.remove(10)
    assert 10 not in s
    with pytest.raises(KeyError):
        s.remove(10)


def test_set_replace():
    s = MutableSet()
    s.from_list([1, 2, 3])
    s.set(2, 20)
    assert 2 not in s
    assert 20 in s
    with pytest.raises(KeyError):
        s.set(999, 1)


def test_reverse_noop_for_set():
    s = MutableSet()
    s.from_list([1, 2, 3])
    before = set(s)
    s.reverse()
    assert set(s) == before


def test_from_to_list():
    s = MutableSet()
    s.from_list([1, 2, 2, 3, None])
    assert set(s.to_list()) == {1, 2, 3, None}


def test_filter():
    s = MutableSet()
    s.from_list([1, 2, 3, 4, None])
    s.filter(lambda x: isinstance(x, int) and x % 2 == 0)
    assert set(s) == {2, 4}


def test_map():
    s = MutableSet()
    s.from_list([1, 2, 2, 3])
    s.map(lambda x: x * 10)
    assert set(s) == {10, 20, 30}


def test_reduce():
    s = MutableSet()
    s.from_list([1, 2, 3])
    assert s.reduce(lambda a, b: a + b) == 6
    assert s.reduce(lambda a, b: a + b, 10) == 16
    e = MutableSet()
    with pytest.raises(TypeError):
        e.reduce(lambda a, b: a + b)


def test_iterator():
    s = MutableSet()
    s.from_list([1, 2, 3])
    i = iter(s)
    got = {next(i), next(i), next(i)}
    assert got == {1, 2, 3}


def test_monoid_empty_concat():
    e = MutableSet.empty()
    s1 = MutableSet()
    s2 = MutableSet()
    s1.from_list([1, 2])
    s2.from_list([2, 3])

    e.concat(s1)
    assert e == s1

    s1.concat(MutableSet.empty())
    assert set(s1) == {1, 2}

    left = MutableSet.empty()
    left.concat(s1)
    left.concat(s2)

    right = MutableSet.empty()
    tmp = MutableSet.empty()
    tmp.concat(s2)
    right.concat(s1)
    right.concat(tmp)

    assert left == right


@given(st.lists(st.one_of(st.integers(), st.none())))
def test_property_from_list_uniqueness(lst):
    s = MutableSet()
    s.from_list(lst)
    assert set(s) == set(lst)


# ---------- additional property-based tests ----------

_elems = st.integers(min_value=-100, max_value=100)


@given(st.lists(_elems))
def test_pbt_from_to_list_set_semantics(lst):
    s = MutableSet()
    s.from_list(lst)
    result = s.to_list()
    assert len(result) == len(set(result))
    assert set(result) == set(lst)


@given(st.lists(_elems), _elems)
def test_pbt_add_idempotence(lst, x):
    s = MutableSet()
    s.from_list(lst)
    s.add(x)
    size_after_first = s.size()
    assert s.member(x)
    s.add(x)
    assert s.size() == size_after_first
    assert s.member(x)


@given(st.lists(_elems), _elems)
def test_pbt_remove_membership(lst, x):
    s = MutableSet()
    s.from_list(lst)
    if s.member(x):
        size_before = s.size()
        s.remove(x)
        assert not s.member(x)
        assert s.size() == size_before - 1


@given(st.lists(_elems), st.lists(_elems), st.lists(_elems))
def test_pbt_concat_associative(lst1, lst2, lst3):
    s1 = MutableSet()
    s1.from_list(lst1)
    s2 = MutableSet()
    s2.from_list(lst2)
    s3 = MutableSet()
    s3.from_list(lst3)

    left = MutableSet()
    left.from_list(lst1)
    left.concat(s2)
    left.concat(s3)

    right = MutableSet()
    right.from_list(lst1)
    tmp = MutableSet()
    tmp.from_list(lst2)
    tmp.concat(s3)
    right.concat(tmp)

    assert left == right


@given(st.lists(_elems))
def test_pbt_concat_empty_identity(lst):
    s = MutableSet()
    s.from_list(lst)

    left = MutableSet.empty()
    left.concat(s)
    assert left == s

    s_copy = MutableSet()
    s_copy.from_list(lst)
    s_copy.concat(MutableSet.empty())
    assert s_copy == s


@given(st.lists(_elems))
def test_pbt_map_no_duplicates(lst):
    s = MutableSet()
    s.from_list(lst)
    s.map(lambda x: x % 5)
    result = s.to_list()
    assert len(result) == len(set(result))


@given(st.lists(_elems))
def test_pbt_filter_no_duplicates(lst):
    s = MutableSet()
    s.from_list(lst)
    s.filter(lambda x: x % 2 == 0)
    result = s.to_list()
    assert len(result) == len(set(result))


@given(st.lists(_elems), st.lists(_elems))
def test_pbt_equality_consistency(lst1, lst2):
    s1 = MutableSet()
    s1.from_list(lst1)
    s2 = MutableSet()
    s2.from_list(lst2)
    if s1 == s2:
        assert s1.size() == s2.size()
        for elem in s1:
            assert s2.member(elem)
        for elem in s2:
            assert s1.member(elem)
