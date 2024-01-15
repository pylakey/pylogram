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

from datetime import datetime
from typing import Union

import pylogram
from pylogram import raw, utils
from pylogram import types


class RestrictChatMember:
    async def restrict_chat_member(
        self: "pylogram.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        permissions: "types.ChatPermissions",
        until_date: datetime = utils.zero_datetime()
    ) -> "types.Chat":
        """Restrict a user in a supergroup.

        You must be an administrator in the supergroup for this to work and must have the appropriate admin rights.
        Pass True for all permissions to lift restrictions from a user.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            permissions (:obj:`~pylogram.types.ChatPermissions`):
                New user permissions.

            until_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the user will be unbanned.
                If user is banned for more than 366 days or less than 30 seconds from the current time they are
                considered to be banned forever. Defaults to epoch (ban forever).

        Returns:
            :obj:`~pylogram.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                from datetime import datetime, timedelta
                from pylogram.types import ChatPermissions

                # Completely restrict chat member (mute) forever
                await app.restrict_chat_member(chat_id, user_id, ChatPermissions())

                # Chat member muted for 24h
                await app.restrict_chat_member(chat_id, user_id, ChatPermissions(),
                    datetime.now() + timedelta(days=1))

                # Chat member can only send text messages
                await app.restrict_chat_member(chat_id, user_id,
                    ChatPermissions(can_send_messages=True))
        """
        r = await self.invoke(
            raw.functions.channels.EditBanned(
                channel=await self.resolve_peer(chat_id),
                participant=await self.resolve_peer(user_id),
                banned_rights=raw.types.ChatBannedRights(
                    until_date=utils.datetime_to_timestamp(until_date),
                    view_messages=not permissions.can_view_messages,
                    send_messages=not permissions.can_send_messages,
                    send_media=not permissions.can_send_media,
                    send_stickers=not permissions.can_send_stickers,
                    send_gifs=not permissions.can_send_gifs,
                    send_games=not permissions.can_send_games,
                    send_inline=not permissions.can_send_inline,
                    embed_links=not permissions.can_embed_links,
                    send_polls=not permissions.can_send_polls,
                    change_info=not permissions.can_change_info,
                    invite_users=not permissions.can_invite_users,
                    pin_messages=not permissions.can_pin_messages,
                    manage_topics=not permissions.can_manage_topics,
                    send_photos=not permissions.can_send_photos,
                    send_videos=not permissions.can_send_videos,
                    send_roundvideos=not permissions.can_send_roundvideos,
                    send_audios=not permissions.can_send_audios,
                    send_voices=not permissions.can_send_voices,
                    send_docs=not permissions.can_send_docs,
                    send_plain=not permissions.can_send_plain,
                )
            )
        )

        return types.Chat._parse_chat(self, r.chats[0])
