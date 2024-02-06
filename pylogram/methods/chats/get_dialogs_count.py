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
from pylogram import constants
from pylogram import raw


class GetDialogsCount:
    async def get_dialogs_count(
        self: "pylogram.Client",
        pinned_only: bool = False,
        folder_id: int = None
    ) -> int:
        """Get the total count of your dialogs.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            folder_id (``int``, optional):
                The ID of the folder you wish to get the dialogs count for.
            pinned_only (``bool``, *optional*):
                Pass True if you want to count only pinned dialogs.
                Defaults to False.

        Returns:
            ``int``: On success, the dialogs count is returned.

        Example:
            .. code-block:: python

                count = await app.get_dialogs_count()
                print(count)
        """

        async with self.dialogs_lock:
            if pinned_only:
                return len((await self.invoke(raw.functions.messages.GetPinnedDialogs(folder_id=0))).dialogs)
            else:
                r = await self.invoke(
                    raw.functions.messages.GetDialogs(
                        exclude_pinned=False,
                        offset_date=constants.MAX_INT_32,
                        offset_id=0,  # Offset message ID
                        offset_peer=raw.types.InputPeerEmpty(),  # Offset peer ID
                        limit=1,
                        hash=0,
                        folder_id=folder_id,
                    )
                )

                if isinstance(r, raw.types.messages.Dialogs):
                    return len(r.dialogs)
                else:
                    return r.count
