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
import pylogram.peers
from pylogram import constants, raw, raw_parsers, utils


class DialogsIterator:
    """Async iterator for loading dialogs in batches."""

    def __init__(
        self,
        client: "pylogram.Client",
        sleep_threshold: int = 60,
        batch_size: int = constants.TELEGRAM_MAX_BATCH_SIZE,
        exclude_pinned: bool = False,
        folder_id: int = None,
    ):
        self.client = client
        self.sleep_threshold = sleep_threshold
        self.batch_size = min(batch_size, constants.TELEGRAM_MAX_BATCH_SIZE)
        self.exclude_pinned = exclude_pinned
        self.folder_id = folder_id

        self.already_loaded_peers_ids: set[int] = set()
        self.messages: dict[tuple[int | None, int], raw.base.Message] = {}
        self.users: dict[int, raw.base.User] = {}
        self.chats: dict[int, raw.base.Chat] = {}

        self.total_count = constants.MAX_INT_32
        self.offset_peer = raw.types.InputPeerEmpty()
        self.offset_id = 0
        self.offset_date = 0
        self.finished = False
        self.buffer: list[pylogram.types.Dialog] = []

    def __aiter__(self) -> "DialogsIterator":
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> pylogram.types.Dialog:
        """Return next dialog from iterator."""
        # If buffer has items, return one
        if self.buffer:
            return self.buffer.pop(0)

        # If finished and buffer is empty, stop iteration
        if self.finished:
            raise StopAsyncIteration

        # Fetch next batch and fill buffer
        await self._fetch_next_batch()

        # Try to return from buffer again
        if self.buffer:
            return self.buffer.pop(0)

        # If still no items, we're done
        raise StopAsyncIteration

    async def _fetch_next_batch(self) -> None:
        """Fetch next batch of dialogs and fill buffer."""
        # Check if we've reached the total count
        if len(self.already_loaded_peers_ids) >= self.total_count:
            self.finished = True
            return

        # Fetch next batch
        request = raw.functions.messages.GetDialogs(
            offset_date=self.offset_date,
            offset_id=self.offset_id,
            offset_peer=self.offset_peer,
            limit=self.batch_size,
            hash=0,
            exclude_pinned=self.exclude_pinned,
            folder_id=self.folder_id,
        )
        response: raw.base.messages.Dialogs = await self.client.invoke(
            request,
            sleep_threshold=self.sleep_threshold,
        )
        self.total_count = len(response.dialogs) if isinstance(response, raw.types.messages.Dialogs) else response.count

        if isinstance(response, raw.types.messages.DialogsNotModified):
            self.finished = True
            return

        if not isinstance(response, (raw.types.messages.DialogsSlice, raw.types.messages.Dialogs)):
            raise ValueError(f"Unknown response type: {type(response)}")

        if len(response.dialogs) == 0:
            self.finished = True
            return

        # Update messages, users, chats
        self.messages.update({utils.get_dialog_message_key(m.peer_id, m.id): m for m in response.messages})
        self.users.update({u.id: u for u in response.users})
        self.chats.update({c.id: c for c in response.chats})

        # Process dialogs and find new ones
        new_dialogs = []
        for d in response.dialogs:
            if (peer_id := utils.get_peer_id(d.peer)) not in self.already_loaded_peers_ids:
                self.already_loaded_peers_ids.add(peer_id)
                new_dialogs.append(d)

        if new_dialogs:
            self.buffer.extend(
                raw_parsers.parse_raw_dialogs(
                    self.client,
                    new_dialogs,
                    self.messages,
                    self.users,
                    self.chats,
                )
            )

        # Update pagination params
        if isinstance(response, raw.types.messages.Dialogs):
            self.finished = True
            return

        last_message = next(
            filter(
                None,
                (
                    self.messages.get(utils.get_dialog_message_key(d.peer, d.top_message))
                    for d in reversed(response.dialogs)
                ),
            ),
            None,
        )

        self.offset_id = last_message.id if last_message else 0
        self.offset_date = (
            last_message.date if isinstance(last_message, (raw.types.Message, raw.types.MessageService)) else 0
        )
        self.offset_peer = pylogram.peers.get_input_peer(
            self.buffer[-1].get_raw().peer,
            users=response.users,
            chats=response.chats,
        )


class LoadAllDialogs:
    async def load_all_dialogs(
        self: "pylogram.Client",
        sleep_threshold: int = 60,
        batch_size: int = 100,
        exclude_pinned: bool = False,
        folder_id: int = None,
    ) -> list[pylogram.types.Dialog]:
        async with self.dialogs_lock:
            dialogs_iterator = DialogsIterator(
                client=self,
                sleep_threshold=sleep_threshold,
                batch_size=batch_size,
                exclude_pinned=exclude_pinned,
                folder_id=folder_id,
            )
            self.dialogs = []

            async for dialog in dialogs_iterator:
                self.dialogs.append(dialog)

            return self.dialogs
