from pylogram.updates.types import PendingUpdate


def test_pending_update_start_end():
    u = PendingUpdate(update=object(), pts=105, pts_count=2, users={}, chats={})
    assert u.start == 103
    assert u.end == 105


def test_pending_update_single_count():
    u = PendingUpdate(update=object(), pts=101, pts_count=1, users={}, chats={})
    assert u.start == 100
    assert u.end == 101
