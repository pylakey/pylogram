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
import asyncio
import random

import pylogram


class UpdateDialogFilter:
    async def update_dialog_filter(
            self: "pylogram.Client",
            title: str,
            dialog_filter_id: int | None = None,
            chats: list[int | str | pylogram.raw.base.InputPeer] = None,
            pinned_chats: list[int | str | pylogram.raw.base.InputPeer] = None,
            emoticon: str | None = None,
            color: str | None = None,
    ) -> pylogram.raw.base.DialogFilter | None:
        # NOTICE: Only creation of DialogFilterChatlist is supported
        if bool(dialog_filter_id) and not (2 <= dialog_filter_id <= 255):
            raise ValueError("`chat_list_id` must be an integer between 2 and 255")

        all_filters = await self.get_dialog_filters()
        current_filter = None

        if dialog_filter_id is not None:
            current_filter = next((
                f
                for f in all_filters.filters
                if not isinstance(f, pylogram.raw.types.DialogFilterDefault) and f.id == dialog_filter_id), None
            )
        else:
            all_filters_ids = set([getattr(f, 'id', 0) for f in all_filters.filters])

            while True:
                dialog_filter_id = random.randint(2, 255)
                if dialog_filter_id not in all_filters_ids:
                    break

        pinned_peers = await asyncio.gather(*[
            self.resolve_peer(chat)
            for chat in pinned_chats or []
        ])
        include_peers = await asyncio.gather(*[
            self.resolve_peer(chat)
            for chat in chats or []
        ])

        success = await self.invoke(
            pylogram.raw.functions.messages.UpdateDialogFilter(
                id=dialog_filter_id,
                # noinspection PyTypeChecker
                filter=pylogram.raw.types.DialogFilterChatlist(
                    id=dialog_filter_id,
                    title=title or getattr(current_filter, 'title', str(dialog_filter_id)),
                    pinned_peers=pinned_peers or getattr(current_filter, 'pinned_peers', []),
                    include_peers=include_peers or getattr(current_filter, 'include_peers', []),
                    emoticon=emoticon or getattr(current_filter, 'emoticon', None),
                    color=color or getattr(current_filter, 'color', None),
                )
            )
        )

        if success:
            return await self.get_dialog_filter_by_id(dialog_filter_id)

        return current_filter
