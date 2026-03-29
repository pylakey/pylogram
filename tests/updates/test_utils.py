import pytest
from pylogram import raw
from pylogram.updates.utils import (
    get_update_channel_id,
    get_update_pts,
    get_update_pts_count,
    get_update_qts,
    get_update_type,
)

# Update type constants
TYPE_PTS = 0
TYPE_QTS = 1
TYPE_CHANNEL = 2
TYPE_NONE = 3


def test_new_message_is_pts():
    u = raw.types.UpdateNewMessage(
        message=raw.types.MessageEmpty(id=1),
        pts=100,
        pts_count=1,
    )
    assert get_update_type(u) == TYPE_PTS
    assert get_update_pts(u) == 100
    assert get_update_pts_count(u) == 1


def test_delete_messages_is_pts():
    u = raw.types.UpdateDeleteMessages(messages=[1, 2], pts=100, pts_count=2)
    assert get_update_type(u) == TYPE_PTS


def test_new_channel_message_is_channel():
    u = raw.types.UpdateNewChannelMessage(
        message=raw.types.MessageEmpty(id=1),
        pts=50,
        pts_count=1,
    )
    assert get_update_type(u) == TYPE_CHANNEL
    assert get_update_pts(u) == 50


def test_new_encrypted_message_is_qts():
    u = raw.types.UpdateNewEncryptedMessage(
        message=raw.types.EncryptedMessageService(
            chat_id=1, date=0, bytes=b"", random_id=0
        ),
        qts=10,
    )
    assert get_update_type(u) == TYPE_QTS
    assert get_update_qts(u) == 10


def test_user_status_is_none():
    u = raw.types.UpdateUserStatus(
        user_id=1,
        status=raw.types.UserStatusEmpty(),
    )
    assert get_update_type(u) == TYPE_NONE


def test_channel_id_from_channel_update():
    msg = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChannel(channel_id=42),
        date=0,
        message="hi",
    )
    u = raw.types.UpdateNewChannelMessage(message=msg, pts=1, pts_count=1)
    cid = get_update_channel_id(u)
    assert cid == 42


def test_channel_id_from_delete_channel_messages():
    u = raw.types.UpdateDeleteChannelMessages(
        channel_id=99, messages=[1], pts=1, pts_count=1
    )
    assert get_update_channel_id(u) == 99
