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

from typing import Union

import pylogram
from pylogram import raw
from pylogram import types


class JoinChat:
    async def join_chat(
        self: "pylogram.Client",
        chat_id: Union[int, str]
    ) -> "types.Chat":
        """Join a group chat or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, a username of the target
                channel/supergroup (in the format @username) or a chat id of a linked chat (channel or supergroup).

        Returns:
            :obj:`~pylogram.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                # Join chat via invite link
                await app.join_chat("https://t.me/+AbCdEf0123456789")

                # Join chat via username
                await app.join_chat("pylogram")

                # Join a linked chat
                await app.join_chat(app.get_chat("pylogram").linked_chat.id)
        """

        if bool(match := self.INVITE_LINK_RE.match(str(chat_id))):
            invite_hash = match.group(1)
            chat_invite = await self.invoke(
                raw.functions.messages.CheckChatInvite(
                    hash=invite_hash
                )
            )

            if isinstance(chat_invite, raw.types.ChatInviteAlready):
                chat = chat_invite.chat
            else:
                result = await self.invoke(
                    raw.functions.messages.ImportChatInvite(
                        hash=invite_hash
                    )
                )
                chat = result.chats[0]
        else:
            result = await self.invoke(
                raw.functions.channels.JoinChannel(
                    channel=await self.resolve_peer(chat_id)
                )
            )
            chat = result.chats[0]

        if isinstance(chat, raw.types.Chat):
            # noinspection PyProtectedMember
            return types.Chat._parse_chat_chat(self, chat)
        elif isinstance(chat, raw.types.Channel):
            # noinspection PyProtectedMember
            return types.Chat._parse_channel_chat(self, chat)
