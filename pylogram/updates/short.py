"""Convert UpdateShortMessage / UpdateShortChatMessage to UpdateNewMessage.

Approach (hybrid Android + gotd/td):
- Check peer cache first (Android). If any required peer is missing, return None
  so the caller can call getDifference instead.
- Synthesise a raw.types.Message from available fields (Android).
- Wrap as UpdateNewMessage and route through the normal pts SequenceBox (gotd/td).
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pylogram import raw

log = logging.getLogger(__name__)


async def convert_short_update(
    update: raw.types.UpdateShortMessage | raw.types.UpdateShortChatMessage,
    get_peer: Callable[[int], Awaitable[Any | None]],
    my_user_id: int,
) -> raw.types.UpdateNewMessage | None:
    """Convert a short update to UpdateNewMessage.

    Returns None if any required peer is missing from cache — caller should
    call getDifference to get the full update with all peer objects.
    """
    if isinstance(update, raw.types.UpdateShortMessage):
        return await _convert_short_message(update, get_peer, my_user_id)
    if isinstance(update, raw.types.UpdateShortChatMessage):
        return await _convert_short_chat_message(update, get_peer, my_user_id)
    return None


async def _convert_short_message(
    update: raw.types.UpdateShortMessage,
    get_peer: Callable[[int], Awaitable[Any | None]],
    my_user_id: int,
) -> raw.types.UpdateNewMessage | None:
    if await get_peer(update.user_id) is None:
        log.debug(
            "UpdateShortMessage: user %d not in cache, falling back to getDifference",
            update.user_id,
        )
        return None

    for entity in update.entities or []:
        if isinstance(entity, raw.types.MessageEntityMentionName):
            if await get_peer(entity.user_id) is None:
                log.debug("UpdateShortMessage: mentioned user %d not in cache", entity.user_id)
                return None

    from_id = my_user_id if update.out else update.user_id

    message = raw.types.Message(
        id=update.id,
        from_id=raw.types.PeerUser(user_id=from_id),
        peer_id=raw.types.PeerUser(user_id=update.user_id),
        message=update.message,
        date=update.date,
        out=update.out or False,
        mentioned=update.mentioned or False,
        media_unread=update.media_unread or False,
        silent=update.silent or False,
        entities=update.entities,
        fwd_from=update.fwd_from,
        via_bot_id=update.via_bot_id,
        reply_to=update.reply_to,
        ttl_period=update.ttl_period,
        media=raw.types.MessageMediaEmpty(),
    )
    return raw.types.UpdateNewMessage(
        message=message,
        pts=update.pts,
        pts_count=update.pts_count,
    )


async def _convert_short_chat_message(
    update: raw.types.UpdateShortChatMessage,
    get_peer: Callable[[int], Awaitable[Any | None]],
    my_user_id: int,
) -> raw.types.UpdateNewMessage | None:
    from_id = my_user_id if update.out else update.from_id

    if not update.out and await get_peer(update.from_id) is None:
        log.debug("UpdateShortChatMessage: user %d not in cache", update.from_id)
        return None

    if await get_peer(update.chat_id) is None:
        log.debug("UpdateShortChatMessage: chat %d not in cache", update.chat_id)
        return None

    for entity in update.entities or []:
        if isinstance(entity, raw.types.MessageEntityMentionName):
            if await get_peer(entity.user_id) is None:
                return None

    message = raw.types.Message(
        id=update.id,
        from_id=raw.types.PeerUser(user_id=from_id),
        peer_id=raw.types.PeerChat(chat_id=update.chat_id),
        message=update.message,
        date=update.date,
        out=update.out or False,
        mentioned=update.mentioned or False,
        media_unread=update.media_unread or False,
        silent=update.silent or False,
        entities=update.entities,
        fwd_from=update.fwd_from,
        via_bot_id=update.via_bot_id,
        reply_to=update.reply_to,
        ttl_period=update.ttl_period,
        media=raw.types.MessageMediaEmpty(),
    )
    return raw.types.UpdateNewMessage(
        message=message,
        pts=update.pts,
        pts_count=update.pts_count,
    )
