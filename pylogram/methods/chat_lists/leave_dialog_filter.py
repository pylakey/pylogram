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


class LeaveDialogFilter:
    async def leave_dialog_filter(
            self: "pylogram.Client",
            dialog_filter: int | pylogram.raw.base.DialogFilter,
            leave_chats: bool = True
    ):
        if isinstance(dialog_filter, int):
            dialog_filter = await self.get_dialog_filter_by_id(dialog_filter)

            if not bool(dialog_filter):
                raise ValueError("Dialog filter with this ID not found.")

        await self.invoke(
            pylogram.raw.functions.chatlists.LeaveChatlist(
                chatlist=pylogram.raw.types.InputChatlistDialogFilter(
                    filter_id=dialog_filter.id
                ),
                peers=dialog_filter.include_peers if leave_chats else []
            )
        )
