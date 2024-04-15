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
from pylogram import utils


class EditExportedInvite:
    async def edit_exported_invite(
            self: "pylogram.Client",
            invite_url: str,
            dialog_filter_id: int,
            title: str | None = None,
            peers: list[pylogram.raw.base.InputPeer] | None = None
    ) -> pylogram.raw.base.ExportedChatlistInvite:
        return await self.invoke(
            pylogram.raw.functions.chatlists.EditExportedInvite(
                chatlist=pylogram.raw.types.InputChatlistDialogFilter(
                    filter_id=dialog_filter_id
                ),
                slug=utils.chat_list_invite_link_to_slug(invite_url),
                title=title,
                peers=peers or []
            )
        )
