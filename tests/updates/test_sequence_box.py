from pylogram.updates.sequence_box import SequenceBox
from pylogram.updates.types import PendingUpdate


def _u(pts: int, count: int, obj=None) -> PendingUpdate:
    return PendingUpdate(update=obj or object(), pts=pts, pts_count=count, users={}, chats={})


# --- check_gap logic ---

def test_apply_when_exactly_next():
    box = SequenceBox()
    box.state = 100
    result = box.feed(_u(101, 1))
    assert result is not None
    assert len(result) == 1
    assert box.state == 101


def test_ignore_duplicate():
    box = SequenceBox()
    box.state = 100
    result = box.feed(_u(100, 1))  # start=99, end=100: 100+1 > 100 → ignore
    assert result is None
    assert box.state == 100


def test_ignore_old_update():
    box = SequenceBox()
    box.state = 100
    # pts=95, count=2 → start=93, end=95: local(100)+count(2)=102 > remote(95) → ignore
    result = box.feed(_u(95, 2))
    assert result is None
    assert box.state == 100


def test_gap_detected_buffers_update():
    box = SequenceBox()
    box.state = 100
    # pts=105, count=2 → start=103; local(100)+count(2)=102 ≠ 105 → gap
    result = box.feed(_u(105, 2))
    assert result is None
    assert box.has_gap
    assert box.state == 100  # state unchanged


def test_gap_filled_by_subsequent_update():
    box = SequenceBox()
    box.state = 100
    # First: gap detected at [100, 103)
    assert box.feed(_u(105, 2)) is None  # gap [100, 103)
    # Second: fills the gap — pts=103, count=3 covers [100, 103)
    result = box.feed(_u(103, 3))
    assert result is not None
    # Should deliver both updates in order
    assert len(result) == 2
    assert result[0].pts == 103  # the filling update
    assert result[1].pts == 105  # the buffered out-of-order update
    assert box.state == 105
    assert not box.has_gap


def test_gap_fills_without_pending_returns_nothing():
    box = SequenceBox()
    box.state = 100
    # Gap: [100, 103), buffered update at pts=105
    assert box.feed(_u(105, 2)) is None
    # Partial fill: covers [101, 103) only — gap [100, 101) remains
    result = box.feed(_u(103, 2))
    assert result is None  # gap still open
    assert box.has_gap


def test_apply_difference_clears_gap_and_drains():
    box = SequenceBox()
    box.state = 100
    # Create gap with buffered update
    assert box.feed(_u(105, 2)) is None
    assert box.has_gap
    # getDifference delivered — advance to new state
    drained = box.apply_difference(105)
    assert not box.has_gap
    assert box.state == 105
    # The buffered update pts=105 is now a duplicate — should be drained or ignored
    assert len(drained) == 0


def test_apply_difference_drains_pending_in_order():
    box = SequenceBox()
    box.state = 100
    # Buffer pts=105 (gap) and pts=107
    box.feed(_u(105, 2))
    box.feed(_u(107, 2))
    # getDifference fills up to 105
    drained = box.apply_difference(105)
    # pts=107 is now next (105+2==107) — should be drained
    assert len(drained) == 1
    assert drained[0].pts == 107
    assert box.state == 107


def test_qts_zero_always_applies():
    box = SequenceBox()
    box.state = 100
    # remote_state=0 means "apply unconditionally" (qts edge case)
    result = box.feed(_u(0, 0))
    assert result is not None
