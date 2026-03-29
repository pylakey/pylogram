from __future__ import annotations

from typing import Literal, TYPE_CHECKING

from .gap_buffer import GapBuffer

if TYPE_CHECKING:
    from .types import PendingUpdate


def _check_gap(
    local_state: int,
    remote_state: int,
    count: int,
) -> Literal["apply", "ignore", "gap"]:
    """Classify an incoming update relative to local sequence state.

    apply  — this is exactly the next expected update
    ignore — this update is a duplicate or already-seen (drop it)
    gap    — there are missing updates between local_state and this one
    """
    if remote_state == 0:
        return "apply"                          # qts edge case (no ordering)
    if local_state + count == remote_state:
        return "apply"                          # perfectly sequential
    if local_state + count > remote_state:
        return "ignore"                         # duplicate or old
    return "gap"                                # missing updates detected


class SequenceBox:
    """Gap-tracking state machine for one sequence space (pts, qts, or seq).

    Purely synchronous — no asyncio dependencies. The caller is responsible
    for starting gap timers and calling getDifference.

    Usage::

        box = SequenceBox()
        box.state = initial_pts  # set from persisted state or getState result

        result = box.feed(pending_update)
        if result is not None:
            for u in result:
                deliver(u.update, u.users, u.chats)
        elif box.has_gap:
            # start/restart gap timer
    """

    __slots__ = ("state", "_gaps", "_pending")

    def __init__(self) -> None:
        self.state: int = 0
        self._gaps = GapBuffer()
        self._pending: list[PendingUpdate] = []

    @property
    def has_gap(self) -> bool:
        """True when gap detection is active and waiting for missing updates."""
        return self._gaps.has_gaps()

    def feed(self, update: PendingUpdate) -> list[PendingUpdate] | None:
        """Process an incoming update.

        Returns a list of updates ready to deliver (ordered by pts), or None
        if the update was buffered (gap mode) or dropped (duplicate).
        """
        result = _check_gap(self.state, update.pts, update.pts_count)

        if result == "ignore":
            return None

        if result == "apply":
            self.state = update.end
            # Drain any buffered updates that are now in sequence
            drained = self._drain_pending()
            return [update] + drained

        # GAP detected
        self._pending.append(update)

        if not self._gaps.has_gaps():
            # Transition to gap mode: gap range is [current_state, update.start)
            self._gaps.enable(self.state, update.start)
            # Try to fill with already-buffered updates
            for p in self._pending:
                self._gaps.consume(p)

            if not self._gaps.has_gaps():
                # Pending updates filled the entire gap — apply all
                return self._drain_pending()
            # Gap remains — caller must start timer
            return None
        else:
            # Already in gap mode — try to consume this new update
            self._gaps.consume(update)
            if not self._gaps.has_gaps():
                # Gap fully filled — apply pending
                return self._drain_pending()
            return None

    def apply_difference(self, new_state: int) -> list[PendingUpdate]:
        """Apply getDifference completion.

        Clears gaps, advances state to new_state, drains any pending updates
        that are now applicable. Returns drained updates to deliver.
        """
        self._gaps.clear()
        self.state = new_state
        return self._drain_pending()

    def _drain_pending(self) -> list[PendingUpdate]:
        """Apply all consecutively-ordered pending updates from current state."""
        self._pending.sort(key=lambda u: u.start)
        applied: list[PendingUpdate] = []
        remaining: list[PendingUpdate] = []

        for u in self._pending:
            check = _check_gap(self.state, u.pts, u.pts_count)
            if check == "apply":
                self.state = u.end
                applied.append(u)
            elif check == "gap":
                remaining.append(u)
            # ignore: drop silently

        self._pending = remaining

        # If state has advanced past all tracked gap ranges, clear them
        if not self._pending and self._gaps.has_gaps():
            self._gaps.clear()

        return applied
