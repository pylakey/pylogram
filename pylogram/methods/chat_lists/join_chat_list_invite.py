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
from pylogram import utils
from pylogram.raw.base.chatlists import ChatlistInvite
from pylogram.raw.types.chatlists import ChatlistInviteAlready


class JoinChatListInvite:
    async def join_chats_list_invite(
            self: "pylogram.Client",
            invite_link: str,
            auto_join_updates: bool = True
    ):
        chats_list_invite = await self.check_chat_list_invite(invite_link)

        if isinstance(chats_list_invite, ChatlistInvite):
            peers = await asyncio.gather(*[
                self.resolve_peer(utils.get_peer_id(p))
                for p in chats_list_invite.peers
            ])
            # noinspection PyTypeChecker
            await self.invoke(
                pylogram.raw.functions.chatlists.JoinChatlistInvite(
                    slug=utils.chat_list_invite_link_to_slug(invite_link),
                    peers=peers
                )
            )
        elif auto_join_updates and isinstance(chats_list_invite, ChatlistInviteAlready):
            await self.join_chat_list_updates(chats_list_invite.filter_id)
