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


class JoinChatListInvite:
    async def join_chat_list_invite(
            self: "pylogram.Client",
            invite_link: str,
            auto_join_updates: bool = True
    ) -> pylogram.raw.base.Updates | None:
        slug = pylogram.utils.chat_list_invite_link_to_slug(invite_link)
        cli = await self.invoke(pylogram.raw.functions.chatlists.CheckChatlistInvite(slug=slug))
        chats_by_id: dict[int, pylogram.raw.base.Chat] = {c.id: c for c in cli.chats}
        users_by_id: dict[int, pylogram.raw.base.User] = {u.id: u for u in cli.users}

        if isinstance(cli, pylogram.raw.types.chatlists.ChatlistInvite):
            peers = cli.peers
        elif isinstance(cli, pylogram.raw.types.chatlists.ChatlistInviteAlready) and auto_join_updates:
            peers = cli.missing_peers
        else:
            peers = []

        peers_to_join = []

        for p in peers:
            if p := pylogram.utils.get_input_peer_from_peer(p, chats=chats_by_id, users=users_by_id, allowed_only=True):
                peers_to_join.append(p)

        if len(peers_to_join) > 0:
            return await self.invoke(
                pylogram.raw.functions.chatlists.JoinChatlistInvite(
                    slug=slug,
                    peers=peers_to_join
                )
            )

        return None
