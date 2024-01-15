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


class RevokeChatInviteLink:
    async def revoke_chat_invite_link(
        self: "pylogram.Client",
        chat_id: Union[int, str],
        invite_link: str,
    ) -> "types.ChatInviteLink":
        """Revoke a previously created invite link.

        If the primary link is revoked, a new link is automatically generated.

        You must be an administrator in the chat for this to work and must have the appropriate admin rights.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat or username of the target channel/supergroup
                (in the format @username).

            invite_link (``str``):
               The invite link to revoke.

        Returns:
            :obj:`~pylogram.types.ChatInviteLink`: On success, the invite link object is returned.
        """

        r = await self.invoke(
            raw.functions.messages.EditExportedChatInvite(
                peer=await self.resolve_peer(chat_id),
                link=invite_link,
                revoked=True
            )
        )

        users = {i.id: i for i in r.users}

        chat_invite = (
            r.new_invite
            if isinstance(r, raw.types.messages.ExportedChatInviteReplaced)
            else r.invite
        )

        return types.ChatInviteLink._parse(self, chat_invite, users)
