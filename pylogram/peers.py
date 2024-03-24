from pylogram import raw


def get_input_peer(
        peer: raw.base.Peer,
        *,
        users: list[raw.base.User] = None,
        chats: list[raw.base.Chat] = None
) -> raw.base.InputPeer:
    if users is None:
        users = []
    if chats is None:
        chats = []

    if isinstance(peer, raw.types.PeerUser):
        return raw.types.InputPeerUser(
            user_id=peer.user_id,
            access_hash=next(user.access_hash for user in users if user.id == peer.user_id) or 0,
        )
    elif isinstance(peer, raw.types.PeerChat):
        return raw.types.InputPeerChat(
            chat_id=peer.chat_id,
        )
    elif isinstance(peer, raw.types.PeerChannel):
        return raw.types.InputPeerChannel(
            channel_id=peer.channel_id,
            access_hash=next(channel.access_hash for channel in chats if channel.id == peer.channel_id) or 0,
        )
    else:
        return raw.types.InputPeerEmpty()


def get_dialog_input_peer(
        dialog: raw.types.Dialog,
        *,
        users: list[raw.base.User] = None,
        chats: list[raw.base.Chat] = None
) -> raw.base.InputPeer:
    return get_input_peer(dialog.peer, users=users, chats=chats)


def get_chat_input_peer(chat: raw.base.Chat) -> raw.base.InputPeer:
    if isinstance(chat, raw.types.Channel):
        return raw.types.InputPeerChannel(
            channel_id=chat.id,
            access_hash=chat.access_hash or 0
        )
    elif isinstance(chat, raw.types.Chat):
        return raw.types.InputPeerChat(
            chat_id=chat.id
        )

    return raw.types.InputPeerEmpty()


def get_user_input_peer(user: raw.base.User) -> raw.base.InputPeer:
    if isinstance(user, raw.types.User):
        return raw.types.InputPeerUser(
            user_id=user.id,
            access_hash=user.access_hash or 0
        )

    return raw.types.InputPeerEmpty()


def get_resolved_peer_input_peer(
        resolved_peer: raw.base.contacts.ResolvedPeer,
) -> raw.base.InputPeer:
    return get_input_peer(resolved_peer.peer, users=resolved_peer.users, chats=resolved_peer.chats)
