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
from pylogram import raw, types

from ... import utils
from ..object import Object


class Dialog(Object[raw.base.Dialog]):
    """A user's dialog.

    Parameters:
        chat (:obj:`~pylogram.types.Chat`):
            Conversation the dialog belongs to.

        top_message (:obj:`~pylogram.types.Message`):
            The last message sent in the dialog at this time.

        unread_messages_count (``int``):
            Amount of unread messages in this dialog.

        unread_mentions_count (``int``):
            Amount of unread messages containing a mention in this dialog.

        unread_mark (``bool``):
            True, if the dialog has the unread mark set.

        is_pinned (``bool``):
            True, if the dialog is pinned.
    """

    def __init__(
        self,
        *,
        client: "pylogram.Client" = None,
        chat: "types.Chat",
        top_message: "types.Message",
        unread_messages_count: int,
        unread_mentions_count: int,
        unread_mark: bool,
        is_pinned: bool,
        _raw: "raw.base.Dialog" = None,
    ):
        super().__init__(client, _raw=_raw)

        self.chat = chat
        self.top_message = top_message
        self.unread_messages_count = unread_messages_count
        self.unread_mentions_count = unread_mentions_count
        self.unread_mark = unread_mark
        self.is_pinned = is_pinned

    @staticmethod
    def _parse(client, dialog: "raw.types.Dialog", messages, users, chats) -> "Dialog":
        return Dialog(
            chat=types.Chat._parse_dialog(client, dialog.peer, users, chats),
            top_message=messages.get(utils.get_peer_id(dialog.peer)),
            unread_messages_count=dialog.unread_count,
            unread_mentions_count=dialog.unread_mentions_count,
            unread_mark=dialog.unread_mark,
            is_pinned=dialog.pinned,
            client=client,
            _raw=dialog,
        )
