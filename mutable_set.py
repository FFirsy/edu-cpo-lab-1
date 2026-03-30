"""
Mutable set implemented as a hash map with separate chaining.
All mutating operations modify the object in-place.
"""

from typing import Any, Callable, Iterator, List, Optional, Iterable


class MutableSet:
    """
    A mutable set using separate chaining with dynamic resizing.
    """

    def __init__(self, capacity: int = 16, load_factor: float = 0.75):
        self._capacity = capacity
        self._load_factor = load_factor
        self._buckets: List[List[Any]] = [[] for _ in range(capacity)]
        self._size = 0

    # ---------- private helpers ----------
    def _hash(self, element: Any) -> int:
        """Return bucket index for element."""
        return hash(element) % self._capacity

    def _resize(self) -> None:
        """Double capacity if load factor exceeded."""
        if self._size / self._capacity <= self._load_factor:
            return
        new_capacity = self._capacity * 2
        new_buckets: List[List[Any]] = [[] for _ in range(new_capacity)]
        for bucket in self._buckets:
            for elem in bucket:
                idx = hash(elem) % new_capacity
                new_buckets[idx].append(elem)
        self._buckets = new_buckets
        self._capacity = new_capacity

    # ---------- public API ----------
    def add(self, element: Any) -> None:
        """Add element to set (no duplicates)."""
        idx = self._hash(element)
        if element in self._buckets[idx]:
            return
        self._buckets[idx].append(element)
        self._size += 1
        self._resize()

    def remove(self, element: Any) -> None:
        """Remove element; raise KeyError if not present."""
        idx = self._hash(element)
        bucket = self._buckets[idx]
        try:
            bucket.remove(element)
        except ValueError:
            raise KeyError(f"Element {element} not found")
        self._size -= 1

    def member(self, element: Any) -> bool:
        """Check if element is in the set."""
        idx = self._hash(element)
        return element in self._buckets[idx]

    def size(self) -> int:
        """Return number of elements."""
        return self._size

    def to_list(self) -> List[Any]:
        """Convert set to list (order not guaranteed)."""
        return list(self)

    def from_list(self, lst: Iterable[Any]) -> None:
        """Replace set with elements from iterable (unique)."""
        self.clear()
        for elem in lst:
            self.add(elem)

    def clear(self) -> None:
        """Remove all elements."""
        for bucket in self._buckets:
            bucket.clear()
        self._size = 0

    def filter(self, predicate: Callable[[Any], bool]) -> None:
        """Keep only elements satisfying predicate."""
        for bucket in self._buckets:
            # Build new bucket with kept elements
            kept = [elem for elem in bucket if predicate(elem)]
            self._size -= len(bucket) - len(kept)
            bucket.clear()
            bucket.extend(kept)

    def map(self, func: Callable[[Any], Any]) -> None:
        """
        Replace each element by func(element) and keep unique results.
        """
        new_elements = {func(elem) for elem in self}
        self.clear()
        for elem in new_elements:
            self.add(elem)

    def reduce(self, func: Callable[[Any, Any], Any],
               initial: Optional[Any] = None) -> Any:
        """
        Reduce set to a single value using func.
        If initial is omitted, uses first element (raises on empty set).
        """
        it = iter(self)
        if initial is None:
            try:
                acc = next(it)
            except StopIteration:
                raise TypeError("reduce of empty set with no initial value")
        else:
            acc = initial
        for elem in it:
            acc = func(acc, elem)
        return acc

    def __iter__(self) -> Iterator[Any]:
        """Iterator over all elements."""
        for bucket in self._buckets:
            yield from bucket

    # ---------- monoid interface ----------
    @staticmethod
    def empty() -> "MutableSet":
        """Return a new empty set."""
        return MutableSet()

    def concat(self, other: "MutableSet") -> None:
        """Add all elements from other into this set (union)."""
        for elem in other:
            self.add(elem)

    # ---------- convenience methods ----------
    def __len__(self) -> int:
        return self.size()

    def __contains__(self, element: Any) -> bool:
        return self.member(element)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MutableSet):
            return False
        return set(self) == set(other)

    def __repr__(self) -> str:
        return f"MutableSet({self.to_list()})"