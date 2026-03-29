import pytest
from unittest.mock import AsyncMock, MagicMock
from pylogram import raw
from pylogram.updates.short import convert_short_update


async def _found_peer(user_id: int):
    return MagicMock()  # peer object


async def _missing_peer(user_id: int):
    return None


@pytest.mark.asyncio
async def test_short_message_synthesizes_update_new_message():
    short = raw.types.UpdateShortMessage(
        id=42,
        user_id=123,
        message="Hello",
        pts=101,
        pts_count=1,
        date=1000000,
        out=False,
    )
    result = await convert_short_update(short, get_peer=_found_peer, my_user_id=999)
    assert result is not None
    assert isinstance(result, raw.types.UpdateNewMessage)
    assert result.pts == 101
    assert result.pts_count == 1
    msg = result.message
    assert msg.id == 42
    assert msg.message == "Hello"
    assert msg.date == 1000000
    assert isinstance(msg.media, raw.types.MessageMediaEmpty)


@pytest.mark.asyncio
async def test_short_message_out_flag_sets_from_id_to_my_user():
    short = raw.types.UpdateShortMessage(
        id=1,
        user_id=123,
        message="Hi",
        pts=101,
        pts_count=1,
        date=1000000,
        out=True,
    )
    result = await convert_short_update(short, get_peer=_found_peer, my_user_id=999)
    assert result is not None
    msg = result.message
    # When out=True, from_id should be my user
    assert msg.from_id.user_id == 999


@pytest.mark.asyncio
async def test_short_message_missing_peer_returns_none():
    short = raw.types.UpdateShortMessage(
        id=1,
        user_id=123,
        message="Hi",
        pts=101,
        pts_count=1,
        date=1000000,
        out=False,
    )
    result = await convert_short_update(short, get_peer=_missing_peer, my_user_id=999)
    assert result is None


@pytest.mark.asyncio
async def test_short_chat_message_synthesizes_correctly():
    short = raw.types.UpdateShortChatMessage(
        id=10,
        from_id=55,
        chat_id=200,
        message="Group msg",
        pts=50,
        pts_count=1,
        date=2000000,
        out=False,
    )

    async def found(uid):
        return MagicMock()

    result = await convert_short_update(short, get_peer=found, my_user_id=999)
    assert result is not None
    assert isinstance(result, raw.types.UpdateNewMessage)
    msg = result.message
    assert msg.id == 10
    assert msg.from_id.user_id == 55
    assert msg.peer_id.chat_id == 200


@pytest.mark.asyncio
async def test_short_chat_message_missing_chat_returns_none():
    short = raw.types.UpdateShortChatMessage(
        id=10,
        from_id=55,
        chat_id=200,
        message="Group msg",
        pts=50,
        pts_count=1,
        date=2000000,
        out=False,
    )

    call_count = 0

    async def get_peer(uid: int):
        nonlocal call_count
        call_count += 1
        if uid == 200:  # chat not found
            return None
        return MagicMock()

    result = await convert_short_update(short, get_peer=get_peer, my_user_id=999)
    assert result is None
