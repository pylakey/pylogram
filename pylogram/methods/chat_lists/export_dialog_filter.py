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


class ExportDialogFilter:
    async def export_dialog_filter(
            self: "pylogram.Client",
            dialog_filter: pylogram.raw.base.DialogFilter
    ) -> pylogram.raw.base.ExportedChatlistInvite:
        if isinstance(dialog_filter, pylogram.raw.types.DialogFilterChatlist) and dialog_filter.has_my_invites:
            exported_invites = await self.get_exported_invites(dialog_filter.id)

            if len(exported_invites) > 0:
                return await self.edit_exported_invite(
                    exported_invites.invites[0].url,
                    dialog_filter.id,
                    dialog_filter.title,
                    peers=dialog_filter.include_peers
                )

        return await self.export_dialog_filter_invite(dialog_filter)
