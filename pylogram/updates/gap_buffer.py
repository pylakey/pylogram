from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import PendingUpdate


class GapBuffer:
    """Tracks missing ranges in a sequence space using interval subtraction.

    Represents a set of gaps as non-overlapping half-open intervals [from, to).
    An incoming update 'consumes' the part of a gap it covers.
    When has_gaps() is False, all missing updates have arrived.
    """

    __slots__ = ("_gaps",)

    def __init__(self) -> None:
        self._gaps: list[tuple[int, int]] = []

    def enable(self, from_: int, to: int) -> None:
        """Create the initial gap range [from_, to).

        Must be called with no active gaps.
        """
        assert not self._gaps, "GapBuffer already has active gaps"
        self._gaps.append((from_, to))

    def consume(self, update: PendingUpdate) -> bool:
        """Subtract the update's range [start, end) from active gaps.

        Returns True if any gap was intersected (update was within or overlapping
        a gap range). Returns False if the update is entirely outside all gaps.
        """
        u_start = update.start
        u_end = update.end
        new_gaps: list[tuple[int, int]] = []
        consumed = False

        for gap_from, gap_to in self._gaps:
            # No overlap: update is entirely before or after this gap
            if u_end <= gap_from or u_start >= gap_to:
                new_gaps.append((gap_from, gap_to))
                continue

            consumed = True
            # Left remainder: [gap_from, u_start) if any
            if u_start > gap_from:
                new_gaps.append((gap_from, u_start))
            # Right remainder: [u_end, gap_to) if any
            if u_end < gap_to:
                new_gaps.append((u_end, gap_to))

        self._gaps = new_gaps
        return consumed

    def has_gaps(self) -> bool:
        """Return True if any unfilled gaps remain."""
        return bool(self._gaps)

    def clear(self) -> None:
        """Remove all gaps (called before getDifference)."""
        self._gaps.clear()
