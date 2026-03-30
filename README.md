# group4 - lab 1 - variant 4

This project implements a mutable set using a hash map with separate chaining.  
All operations modify the set in place, as required by the laboratory course.  
The implementation handles `None` values, mixed types, and provides the full  
API specified for the assignment.

## Project structure

- `mutable_set.py` – MutableSet class implementation
- `test_mutable_set.py` – Unit and property-based tests

## Features

- **Mutable operations** – `add`, `remove`, `filter`, `map`, `concat` all  
  modify the set in place.
- **Separate chaining** – Each bucket is a Python list; dynamic resizing  
  when load factor exceeds 0.75.
- **Full API support**:
   - `add(elem)`, `remove(elem)`, `member(elem)`, `size()`
   - `to_list()` / `from_list(lst)`
   - `filter(predicate)`, `map(function)`, `reduce(function, initial)`
   - Iterator protocol (`__iter__`)
   - Monoid: `empty()` and `concat(other)`
- **Handles special values** – `None` is accepted; mixed types (e.g., `1`  
  and `1.0`) are treated as equal (following Python semantics).
- **Property-based tests** – Using Hypothesis to verify invariants  
  (uniqueness, commutativity of add, filter correctness, monoid laws).
- **CI ready** – GitHub Actions run linters, type checker, and tests  
  automatically.

## Contribution

- **Liu Xuhan** – (949699845@qq.com) – Implementation and documentation
- **Wang Qifan** – (2473497039@qq.com) – Tests

## Changelog

- **2026-03-30 – 6**  
  Fix README.md style.

- **2026-03-30 – 5**  
  Fix code style.

- **2026-03-30 – 4**  
  Fix pycodestyle violations: add two blank lines before top-level functions,  
  replace lambda assignments with named functions, break long lines, and  
  ensure newline at end of files.

- **2026-03-30 – 3**  
  Modify the README.md and add requirements.txt.

- **2026-03-30 – 2**  
  Fix property-based test for reduce: use integer-only strategy to avoid  
  None and mixed types; adjust assertion to compare sum of unique elements.

- **2026-03-30 – 1**  
  Fix test_mixed_types: handle equality of `1` and `1.0`.

- **2026-03-30 – 0**  
  Initial repository setup and first submission.

## Design notes

- **Resizing strategy** – When `size / capacity > load_factor` (0.75),  
  capacity doubles. All existing elements are rehashed into new buckets.
- **Equality of `1` and `1.0`** – Python considers `1 == 1.0` true,  
  so only one of them can be stored. This matches the behavior of  
  built-in `set`.
- **Handling `None`** – `None` is hashable in Python; it is stored and  
  retrieved normally.
- **Monoid implementation** – `empty()` returns a new empty set; `concat`  
  adds all elements of another set into the current one (union).  
  Associativity holds because concatenation is equivalent to set union.
- **Type safety** – No explicit type restrictions; any hashable object  
  can be stored. Mixed types are allowed but may compare equal  
  unintentionally (e.g., `1` and `True`). This is consistent with  
  Python’s dynamic nature.
- **Performance considerations** – Average O(1) for `add`, `member`,  
  `remove` under good hash distribution. Worst-case O(n) if many  
  collisions occur, but separate chaining with resizing mitigates this.
