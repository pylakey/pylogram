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

log = logging.getLogger(__name__)


class ResolvePeer:
    async def resolve_peer(
        self: "pylogram.Client",
        peer_id: Union[int, str]
    ) -> Union[raw.base.InputPeer, raw.base.InputUser, raw.base.InputChannel]:
        """Get the InputPeer of a known peer id.
        Useful whenever an InputPeer type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pylogram.api.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            peer_id (``int`` | ``str``):
                The peer id you want to extract the InputPeer from.
                Can be a direct id (int), a username (str) or a phone number (str).

        Returns:
            ``InputPeer``: On success, the resolved peer id is returned in form of an InputPeer object.

        Raises:
            KeyError: In case the peer doesn't exist in the internal database.
        """

        # TODO: Add support for resolving peer by phone number

        if not self.is_connected:
            # TODO: raise peer not found in storage file
            raise ConnectionError("Client has not been started yet")

        try:
            return await self.storage.get_peer_by_id(peer_id)
        except KeyError:
            if isinstance(peer_id, str):
                if peer_id in ("self", "me"):
                    return raw.types.InputPeerSelf()

                if bool(invite_link_match := self.INVITE_LINK_RE.match(peer_id)):
                    # TODO: Support invite links
                    pass

                peer_id = peer_id.strip('@+ ')

                try:
                    int(peer_id)
                except ValueError:
                    username = utils.parse_username(peer_id)

                    try:
                        return await self.storage.get_peer_by_username(username)
                    except KeyError:
                        await self.invoke(
                            raw.functions.contacts.ResolveUsername(
                                username=username
                            )
                        )

                        try:
                            return await self.storage.get_peer_by_username(peer_id)
                        except KeyError as e:
                            raise PeerIdInvalid from e
                else:
                    try:
                        return await self.storage.get_peer_by_phone_number(peer_id)
                    except KeyError:
                        await self.invoke(
                            raw.functions.contacts.ResolvePhone(
                                phone=peer_id
                            )
                        )

                        try:
                            return await self.storage.get_peer_by_phone_number(peer_id)
                        except KeyError as e:
                            raise PeerIdInvalid from e

            peer_type = utils.get_peer_type(peer_id)

            if peer_type == "user":
                await self.fetch_peers(
                    await self.invoke(
                        raw.functions.users.GetUsers(
                            id=[
                                raw.types.InputUser(
                                    user_id=peer_id,
                                    access_hash=0
                                )
                            ]
                        )
                    )
                )
            elif peer_type == "chat":
                await self.invoke(
                    raw.functions.messages.GetChats(
                        id=[-peer_id]
                    )
                )
            else:
                await self.invoke(
                    raw.functions.channels.GetChannels(
                        id=[
                            raw.types.InputChannel(
                                channel_id=utils.get_channel_id(peer_id),
                                access_hash=0
                            )
                        ]
                    )
                )

            try:
                return await self.storage.get_peer_by_id(peer_id)
            except KeyError as e:
                raise PeerIdInvalid from e
