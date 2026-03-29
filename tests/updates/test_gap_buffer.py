import pytest
from pylogram.updates.gap_buffer import GapBuffer
from pylogram.updates.types import PendingUpdate


def _u(pts: int, count: int) -> PendingUpdate:
    return PendingUpdate(update=object(), pts=pts, pts_count=count, users={}, chats={})


def test_empty_buffer_has_no_gaps():
    b = GapBuffer()
    assert not b.has_gaps()


def test_enable_creates_gap():
    b = GapBuffer()
    b.enable(100, 103)
    assert b.has_gaps()


def test_consume_fills_exact_gap():
    b = GapBuffer()
    b.enable(100, 103)
    # update covers [101, 103) — pts=103, count=2
    consumed = b.consume(_u(103, 2))
    assert consumed
    # Remaining gap: [100, 101)
    assert b.has_gaps()
    # Fill the last piece: pts=101, count=1 covers [100, 101)
    consumed2 = b.consume(_u(101, 1))
    assert consumed2
    assert not b.has_gaps()


def test_consume_fills_entire_gap_at_once():
    b = GapBuffer()
    b.enable(100, 103)
    consumed = b.consume(_u(103, 3))  # covers [100, 103)
    assert consumed
    assert not b.has_gaps()


def test_consume_outside_gap_returns_false():
    b = GapBuffer()
    b.enable(100, 103)
    # update covers [105, 107) — outside the gap
    consumed = b.consume(_u(107, 2))
    assert not consumed
    assert b.has_gaps()


def test_consume_splits_gap():
    b = GapBuffer()
    b.enable(100, 110)
    # update covers [103, 105) — middle of gap
    consumed = b.consume(_u(105, 2))
    assert consumed
    # Should leave [100, 103) and [105, 110)
    assert b.has_gaps()


def test_clear_removes_all_gaps():
    b = GapBuffer()
    b.enable(100, 110)
    b.clear()
    assert not b.has_gaps()


def test_enable_panics_if_gaps_exist():
    b = GapBuffer()
    b.enable(100, 110)
    with pytest.raises(AssertionError):
        b.enable(110, 120)
