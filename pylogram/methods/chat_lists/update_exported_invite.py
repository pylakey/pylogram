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

import pylogram


class UpdateExportedInvite:
    async def update_exported_invite(
            self: "pylogram.Client",
            invite_url: str,
            title: str,
            chats: list[int | str | pylogram.raw.base.InputPeer] = None,
            pinned_chats: list[int | str | pylogram.raw.base.InputPeer] = None,
            emoticon: str | None = None,
    ) -> pylogram.raw.base.ExportedChatlistInvite | None:
        c = await self.check_chat_list_invite(invite_url)

        if not isinstance(c, pylogram.raw.types.chatlists.ChatlistInviteAlready):
            # TODO: Join maybe?
            return None

        dialog_filter = await self.update_dialog_filter(
            title,
            dialog_filter_id=c.filter_id,
            chats=chats,
            pinned_chats=pinned_chats,
            emoticon=emoticon
        )

        return await self.edit_exported_invite(
            invite_url,
            dialog_filter_id=dialog_filter.id,
            title=dialog_filter.title,
            peers=dialog_filter.include_peers
        )
