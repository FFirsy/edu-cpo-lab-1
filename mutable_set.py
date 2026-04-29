from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
)

T = TypeVar("T")
S = TypeVar("S")


class MutableSet(Generic[T]):
    def __init__(self, capacity: int = 16, load_factor: float = 0.75):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if not (0 < load_factor <= 1):
            raise ValueError("load_factor must be in (0, 1]")
        self._capacity = capacity
        self._load_factor = load_factor
        self._buckets: List[List[T]] = [[] for _ in range(capacity)]
        self._size = 0

    # ---------- private helpers ----------
    def _hash(self, element: T) -> int:
        return hash(element) % self._capacity

    def _resize(self) -> None:
        if self._size / self._capacity <= self._load_factor:
            return
        new_capacity = self._capacity * 2
        new_buckets: List[List[T]] = [[] for _ in range(new_capacity)]
        for bucket in self._buckets:
            for elem in bucket:
                idx = hash(elem) % new_capacity
                new_buckets[idx].append(elem)
        self._buckets = new_buckets
        self._capacity = new_capacity

    # ---------- required API ----------
    def add(self, element: T) -> None:
        idx = self._hash(element)
        if element in self._buckets[idx]:
            return
        self._buckets[idx].append(element)
        self._size += 1
        self._resize()

    def set(self, key: T, value: T) -> None:
        if key not in self:
            raise KeyError(f"Element {key} not found")
        self.remove(key)
        self.add(value)

    def remove(self, element: T) -> None:
        idx = self._hash(element)
        bucket = self._buckets[idx]
        try:
            bucket.remove(element)
        except ValueError as exc:
            raise KeyError(f"Element {element} not found") from exc
        self._size -= 1

    def size(self) -> int:
        return self._size

    def member(self, element: T) -> bool:
        idx = self._hash(element)
        return element in self._buckets[idx]

    def reverse(self) -> None:
        return None

    def from_list(self, lst: Iterable[T]) -> None:
        self.clear()
        for elem in lst:
            self.add(elem)

    def to_list(self) -> List[T]:
        return list(self)

    def filter(self, predicate: Callable[[T], bool]) -> None:
        for bucket in self._buckets:
            kept = [elem for elem in bucket if predicate(elem)]
            self._size -= (len(bucket) - len(kept))
            bucket.clear()
            bucket.extend(kept)

    def map(self, func: Callable[[T], Any]) -> None:
        mapped_unique = {func(elem) for elem in self}
        self.clear()
        for elem in mapped_unique:
            self.add(elem)

    def reduce(
        self,
        func: Callable[[S, T], S],
        initial: Optional[S] = None,
    ) -> S:
        it = iter(self)
        if initial is None:
            try:
                acc: S = next(it)  # type: ignore[assignment]
            except StopIteration as exc:
                raise TypeError(
                    "reduce of empty set with no initial value"
                ) from exc
        else:
            acc = initial
        for elem in it:
            acc = func(acc, elem)
        return acc

    # ---------- iterator ----------
    def __iter__(self) -> Iterator[T]:
        for bucket in self._buckets:
            yield from bucket

    # ---------- monoid ----------
    @staticmethod
    def empty() -> "MutableSet[Any]":
        return MutableSet()

    def concat(self, other: "MutableSet[T]") -> None:
        for elem in other:
            self.add(elem)

    # ---------- convenience ----------
    def clear(self) -> None:
        for bucket in self._buckets:
            bucket.clear()
        self._size = 0

    def __len__(self) -> int:
        return self.size()

    def __contains__(self, element: object) -> bool:
        try:
            return self.member(element)  # type: ignore[arg-type]
        except TypeError:
            return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MutableSet):
            return False
        if self._size != other._size:
            return False
        for elem in self:
            if not other.member(elem):
                return False
        return True

    def __repr__(self) -> str:
        return f"MutableSet({self.to_list()})"
