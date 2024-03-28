#  Pylogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2023 Dan <https://github.com/delivrance>
#  Copyright (C) 2023-2024 Pylakey <https://github.com/pylakey>
#
#  This file is part of Pylogram.
#
#  Pylogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pylogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pylogram.  If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Union

import pylogram
from pylogram import raw
from pylogram import utils
from pylogram.errors import PeerIdInvalid
from pylogram.peers import get_chat_input_peer
from pylogram.peers import get_resolved_peer_input_peer
from pylogram.peers import get_user_input_peer
from pylogram.utils import is_tl_object_of_base_type

log = logging.getLogger(__name__)


class ResolvePeer:

    async def _resolve_peer_by_id(
            self: "pylogram.Client",
            peer_id: int,
            cache_only: bool = False
    ) -> raw.base.InputPeer:
        try:
            return await self.storage.get_peer_by_id(peer_id)
        except KeyError:
            if cache_only:
                raise

            peer_type = utils.get_peer_type(peer_id)

            if peer_type == "user":
                users: list[raw.base.User] = await self.invoke(
                    raw.functions.users.GetUsers(
                        id=[
                            raw.types.InputUser(
                                user_id=peer_id,
                                access_hash=0
                            )
                        ]
                    )
                )

                if not users:
                    raise PeerIdInvalid(f"User with id {peer_id} not found")

                await self.update_storage_peers(users)
                return get_user_input_peer(users[0])
            elif peer_type == "chat":
                chats: raw.base.messages.Chats = await self.invoke(
                    raw.functions.messages.GetChats(
                        id=[-peer_id]
                    )
                )
                await self.update_storage_peers(chats.chats)
                return get_chat_input_peer(chats.chats[0])
            elif peer_type == "channel":
                chats: raw.base.messages.Chats = await self.invoke(
                    raw.functions.channels.GetChannels(
                        id=[
                            raw.types.InputChannel(
                                channel_id=utils.get_channel_id(peer_id),
                                access_hash=0
                            )
                        ]
                    )
                )
                await self.update_storage_peers(chats.chats)
                return get_chat_input_peer(chats.chats[0])

        raise ValueError(f"Invalid peer id: {peer_id}")

    async def _resolve_peer_by_username(
            self: "pylogram.Client",
            username: str,
            cache_only: bool = False
    ) -> raw.base.InputPeer | None:
        try:
            return await self.storage.get_peer_by_username(username)
        except KeyError:
            if cache_only:
                raise

            resolved_peer = await self.invoke(
                raw.functions.contacts.ResolveUsername(
                    username=username
                )
            )
            return get_resolved_peer_input_peer(resolved_peer)

    async def _resolve_peer_by_phone_number(
            self: "pylogram.Client",
            phone_number: str,
            cache_only: bool = False
    ) -> raw.base.InputPeer | None:
        try:
            return await self.storage.get_peer_by_phone_number(phone_number)
        except KeyError:
            if cache_only:
                raise

            resolved_peer = await self.invoke(
                raw.functions.contacts.ResolvePhone(
                    phone=phone_number
                )
            )
            return get_resolved_peer_input_peer(resolved_peer)

    async def _resolve_peer_by_invite_hash(self: "pylogram.Client", invite_hash: str, cache_only: bool = False):
        if cache_only:
            # Cache only is not supported for invite links
            raise KeyError(f"Invite link https://t.me/+{invite_hash} not found in cache")

        r: raw.base.ChatInvite = await self.invoke(
            raw.functions.messages.CheckChatInvite(
                hash=invite_hash
            )
        )

        if isinstance(r, raw.types.ChatInvite):
            raise ValueError(f"Invite link https://t.me/+{invite_hash} points to a chat you haven't joined yet")

        await self.update_storage_peers([r.chat])
        return get_chat_input_peer(r.chat)

    async def resolve_peer(
            self: "pylogram.Client",
            peer_info: Union[int, str, raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel],
            *,
            cache_only: bool = False
    ) -> Union[raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel]:
        """Get the InputPeer of a known peer id.
        Useful whenever an InputPeer type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pylogram.api.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            peer_info (``int`` | ``str``):
                The peer id you want to extract the InputPeer from.
                Can be a direct id (int), a username (str) or a phone number (str).

            cache_only (``bool``, *optional*):
                Whether to resolve the peer only if it's already in the internal database.
                Defaults to ``False``.

        Returns:
            ``InputPeer``: On success, the resolved peer id is returned in form of an InputPeer object.

        Raises:
            KeyError: In case the peer doesn't exist in the internal database.
        """

        if is_tl_object_of_base_type(peer_info, (raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel)):
            return peer_info

        if not cache_only and not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        if isinstance(peer_info, int):
            return await self._resolve_peer_by_id(peer_info, cache_only=cache_only)
        elif isinstance(peer_info, str):
            if peer_info in ("self", "me"):
                return raw.types.InputPeerSelf()

            if bool(phone_number := utils.parse_phone_number(peer_info)):
                return await self._resolve_peer_by_phone_number(phone_number, cache_only=cache_only)

            if bool(invite_link_match := self.INVITE_LINK_RE.match(peer_info)):
                return await self._resolve_peer_by_invite_hash(invite_link_match.group(1), cache_only=cache_only)

            if bool(username := utils.parse_username(peer_info)):
                return await self._resolve_peer_by_username(username, cache_only=cache_only)

        raise PeerIdInvalid(f"Invalid peer id: {peer_info}")
