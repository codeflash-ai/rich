from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")


def loop_first(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for first value."""
    iter_values = iter(values)
    try:
        value = next(iter_values)
    except StopIteration:
        return
    yield True, value
    for value in iter_values:
        yield False, value


def loop_last(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    return _iterator_buffered_last(values)


def loop_first_last(values: Iterable[T]) -> Iterable[Tuple[bool, bool, T]]:
    """Iterate and generate a tuple with a flag for first and last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    first = True
    for value in iter_values:
        yield first, False, previous_value
        first = False
        previous_value = value
    yield first, True, previous_value


def _iterator_buffered_last(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Efficient generator that yields (islast, value) from input sequence."""
    it = iter(values)
    try:
        prev = next(it)
    except StopIteration:
        return
    for val in it:
        yield False, prev
        prev = val
    yield True, prev
