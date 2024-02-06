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
from pylogram import raw_parsers
from pylogram import utils


class LoadAllDialogs:
    async def load_all_dialogs(self: "pylogram.Client", sleep_threshold: int = 60) -> list[pylogram.types.Dialog]:
        async with self.dialogs_lock:
            raw_dialogs = []
            already_loaded_peers_ids: set[int] = set()
            messages: dict[tuple[int, int], raw.base.Message] = {}
            users: dict[int, raw.base.User] = {}
            chats: dict[int, raw.base.Chat] = {}
            total_count = constants.MAX_INT_32
            limit = 100
            offset_peer = raw.types.InputPeerEmpty()
            offset_id = 0
            offset_date = 0

            while len(raw_dialogs) < total_count:
                r = await self.invoke(
                    raw.functions.messages.GetDialogs(
                        offset_date=offset_date,
                        offset_id=offset_id,
                        offset_peer=offset_peer,
                        limit=limit,
                        hash=0,
                        exclude_pinned=False,
                        folder_id=None,
                    ),
                    sleep_threshold=sleep_threshold,
                )

                if isinstance(r, raw.types.messages.DialogsNotModified):
                    break

                if len(r.dialogs) == 0:
                    break

                for d in r.dialogs:
                    if (peer_id := utils.get_peer_id(d.peer)) not in already_loaded_peers_ids:
                        already_loaded_peers_ids.add(peer_id)
                        raw_dialogs.append(d)

                messages.update({
                    (utils.get_raw_peer_id(m.peer_id), m.id): m
                    for m in r.messages
                })
                users.update({u.id: u for u in r.users})
                chats.update({c.id: c for c in r.chats})

                if isinstance(r, raw.types.messages.Dialogs):
                    break

                total_count = r.count
                limit = min(100, total_count - len(already_loaded_peers_ids))

                for d in reversed(r.dialogs):
                    if d.top_message:
                        d_top_message = messages.get((utils.get_raw_peer_id(d.peer), d.top_message))

                        if bool(d_top_message):
                            offset_peer = utils.get_dialog_input_peer(d)
                            offset_id = d_top_message.id
                            offset_date = d_top_message.date
                            break

            self.dialogs = raw_parsers.parse_raw_dialogs(self, raw_dialogs, messages, users, chats)
            return self.dialogs
