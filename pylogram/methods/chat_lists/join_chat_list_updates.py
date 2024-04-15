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

import pylogram


class JoinChatListUpdates:
    async def join_chat_list_updates(self: "pylogram.Client", dialog_filter_id: int) -> pylogram.raw.base.Updates:
        updates = await self.get_chat_list_updates(dialog_filter_id)

        # TODO: Implement leaving chats whose are not in folder

        # noinspection PyTypeChecker
        return await self.invoke(
            pylogram.raw.functions.chatlists.JoinChatlistUpdates(
                chatlist=pylogram.raw.types.InputChatlistDialogFilter(
                    filter_id=dialog_filter_id
                ),
                peers=(
                    await asyncio.gather(*[
                        self.resolve_peer(pylogram.utils.get_peer_id(p))
                        for p in updates.missing_peers or []
                    ])
                )
            )
        )
