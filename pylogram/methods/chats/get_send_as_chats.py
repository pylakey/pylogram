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

from typing import List, Union

import pylogram
from pylogram import raw
from pylogram import types


class GetSendAsChats:
    async def get_send_as_chats(
        self: "pylogram.Client",
        chat_id: Union[int, str]
    ) -> List["types.Chat"]:
        """Get the list of "send_as" chats available.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            List[:obj:`~pylogram.types.Chat`]: The list of chats.

        Example:
            .. code-block:: python

                chats = await app.get_send_as_chats(chat_id)
                print(chats)
        """
        r = await self.invoke(
            raw.functions.channels.GetSendAs(
                peer=await self.resolve_peer(chat_id)
            )
        )

        users = {u.id: u for u in r.users}
        chats = {c.id: c for c in r.chats}

        send_as_chats = types.List()

        for p in r.peers:
            if isinstance(p, raw.types.PeerUser):
                send_as_chats.append(types.Chat._parse_chat(self, users[p.user_id]))
            else:
                send_as_chats.append(types.Chat._parse_chat(self, chats[p.channel_id]))

        return send_as_chats
