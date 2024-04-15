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


class GetDialogFilters:
    async def get_dialog_filters(self: "pylogram.Client") -> pylogram.raw.types.messages.DialogFilters:
        # TODO: implement caching?
        return await self.invoke(
            pylogram.raw.functions.messages.GetDialogFilters()
        )

    async def get_dialog_filter_by_id(
            self: "pylogram.Client",
            dialog_filter_id: int
    ) -> pylogram.raw.base.DialogFilter | None:
        all_filters = await self.get_dialog_filters()

        for f in all_filters.filters:
            if getattr(f, 'id', None) == dialog_filter_id:
                return f

        return None

    async def get_dialog_filter_by_title(self: "pylogram.Client", title: str) -> pylogram.raw.base.DialogFilter | None:
        all_filters = await self.get_dialog_filters()

        for f in all_filters.filters:
            if getattr(f, 'title', None) == title:
                return f

        return None
