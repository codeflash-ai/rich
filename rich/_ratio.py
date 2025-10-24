import sys
from fractions import Fraction
from math import ceil
from typing import cast, List, Optional, Sequence

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol  # pragma: no cover


class Edge(Protocol):
    """Any object that defines an edge (such as Layout)."""

    size: Optional[int] = None
    ratio: int = 1
    minimum_size: int = 1


def ratio_resolve(total: int, edges: Sequence[Edge]) -> List[int]:
    """Divide total space to satisfy size, ratio, and minimum_size, constraints.

    The returned list of integers should add up to total in most cases, unless it is
    impossible to satisfy all the constraints. For instance, if there are two edges
    with a minimum size of 20 each and `total` is 30 then the returned list will be
    greater than total. In practice, this would mean that a Layout object would
    clip the rows that would overflow the screen height.

    Args:
        total (int): Total number of characters.
        edges (List[Edge]): Edges within total space.

    Returns:
        List[int]: Number of characters for each edge.
    """
    sizes = [(edge.size or None) for edge in edges]
    _Fraction = Fraction

    # Avoid repeatedly finding flexible edges and summing every iteration
    # Instead dedicate a list for indices of flexible edges and precompute statics
    n_edges = len(edges)

    while True:
        flexible_indices = []
        flexible_ratios = []
        for index in range(n_edges):
            if sizes[index] is None:
                flexible_indices.append(index)
                flexible_ratios.append(edges[index].ratio or 1)

        if not flexible_indices:
            break

        # Precompute sum of fixed sizes
        sum_fixed = 0
        for size in sizes:
            if size is not None:
                sum_fixed += size
        remaining = total - sum_fixed
        if remaining <= 0:
            # No room for flexible edges
            return [
                ((edges[i].minimum_size or 1) if sizes[i] is None else sizes[i])
                for i in range(n_edges)
            ]

        ratio_sum = sum(flexible_ratios)
        portion = _Fraction(remaining, ratio_sum)

        update_needed = False
        for idx_flex, ratio in zip(flexible_indices, flexible_ratios):
            edge = edges[idx_flex]
            if portion * edge.ratio <= edge.minimum_size:
                sizes[idx_flex] = edge.minimum_size
                update_needed = True
                break
        if update_needed:
            continue

        remainder = _Fraction(0)
        for idx_flex, ratio in zip(flexible_indices, flexible_ratios):
            value = portion * ratio + remainder
            size, remainder = divmod(value, 1)
            sizes[idx_flex] = int(size)
        break

    return cast(List[int], sizes)


def ratio_reduce(
    total: int, ratios: List[int], maximums: List[int], values: List[int]
) -> List[int]:
    """Divide an integer total in to parts based on ratios.

    Args:
        total (int): The total to divide.
        ratios (List[int]): A list of integer ratios.
        maximums (List[int]): List of maximums values for each slot.
        values (List[int]): List of values

    Returns:
        List[int]: A list of integers guaranteed to sum to total.
    """
    ratios = [ratio if _max else 0 for ratio, _max in zip(ratios, maximums)]
    total_ratio = sum(ratios)
    if not total_ratio:
        return values[:]
    total_remaining = total
    result: List[int] = []
    append = result.append
    for ratio, maximum, value in zip(ratios, maximums, values):
        if ratio and total_ratio > 0:
            distributed = min(maximum, round(ratio * total_remaining / total_ratio))
            append(value - distributed)
            total_remaining -= distributed
            total_ratio -= ratio
        else:
            append(value)
    return result


def ratio_distribute(
    total: int, ratios: List[int], minimums: Optional[List[int]] = None
) -> List[int]:
    """Distribute an integer total in to parts based on ratios.

    Args:
        total (int): The total to divide.
        ratios (List[int]): A list of integer ratios.
        minimums (List[int]): List of minimum values for each slot.

    Returns:
        List[int]: A list of integers guaranteed to sum to total.
    """
    if minimums:
        ratios = [ratio if _min else 0 for ratio, _min in zip(ratios, minimums)]
    total_ratio = sum(ratios)
    assert total_ratio > 0, "Sum of ratios must be > 0"

    total_remaining = total
    distributed_total: List[int] = []
    append = distributed_total.append
    if minimums is None:
        _minimums = [0] * len(ratios)
    else:
        _minimums = minimums
    for ratio, minimum in zip(ratios, _minimums):
        if total_ratio > 0:
            distributed = max(minimum, ceil(ratio * total_remaining / total_ratio))
        else:
            distributed = total_remaining
        append(distributed)
        total_ratio -= ratio
        total_remaining -= distributed
    return distributed_total


if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class E:
        size: Optional[int] = None
        ratio: int = 1
        minimum_size: int = 1

    resolved = ratio_resolve(110, [E(None, 1, 1), E(None, 1, 1), E(None, 1, 1)])
    print(sum(resolved))
