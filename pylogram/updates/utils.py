"""Update type classification matching Android MessagesController.getUpdateType()."""
from __future__ import annotations

from pylogram import raw


# Type constants (match Android MessagesController getUpdateType())
UPDATE_TYPE_PTS = 0      # global pts-sequenced
UPDATE_TYPE_QTS = 1      # qts-sequenced (encrypted messages)
UPDATE_TYPE_CHANNEL = 2  # per-channel pts
UPDATE_TYPE_NONE = 3     # no sequence number


_PTS_UPDATES = (
    raw.types.UpdateNewMessage,
    raw.types.UpdateDeleteMessages,
    raw.types.UpdateReadHistoryInbox,
    raw.types.UpdateReadHistoryOutbox,
    raw.types.UpdateWebPage,
    raw.types.UpdateReadMessagesContents,
    raw.types.UpdateEditMessage,
    raw.types.UpdatePinnedMessages,
    raw.types.UpdateFolderPeers,
)

_QTS_UPDATES = (
    raw.types.UpdateNewEncryptedMessage,
)

_CHANNEL_UPDATES = (
    raw.types.UpdateNewChannelMessage,
    raw.types.UpdateDeleteChannelMessages,
    raw.types.UpdateEditChannelMessage,
    raw.types.UpdateChannelWebPage,
    raw.types.UpdatePinnedChannelMessages,
)


def get_update_type(update: object) -> int:
    """Return the sequence type of an update (0=pts, 1=qts, 2=channel, 3=none)."""
    if isinstance(update, _PTS_UPDATES):
        return UPDATE_TYPE_PTS
    if isinstance(update, _QTS_UPDATES):
        return UPDATE_TYPE_QTS
    if isinstance(update, _CHANNEL_UPDATES):
        return UPDATE_TYPE_CHANNEL
    return UPDATE_TYPE_NONE


def get_update_pts(update: object) -> int:
    """Return the pts field of an update, or 0 if not present."""
    return getattr(update, "pts", 0)


def get_update_pts_count(update: object) -> int:
    """Return the pts_count field of an update, or 0 if not present."""
    return getattr(update, "pts_count", 0)


def get_update_qts(update: object) -> int:
    """Return the qts field of an update, or 0 if not present."""
    return getattr(update, "qts", 0)


def get_update_channel_id(update: object) -> int | None:
    """Return the channel_id for a channel update, or None."""
    # Direct field (e.g. UpdateDeleteChannelMessages)
    channel_id = getattr(update, "channel_id", None)
    if channel_id:
        return channel_id
    # From message.peer_id (e.g. UpdateNewChannelMessage)
    message = getattr(update, "message", None)
    if message:
        peer_id = getattr(message, "peer_id", None)
        if peer_id:
            return getattr(peer_id, "channel_id", None)
    return None
