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

from typing import List

import pylogram
from pylogram import raw
from pylogram import types
from ..object import Object


class ChatPreview(Object):
    """A chat preview.

    Parameters:
        title (``str``):
            Title of the chat.

        type (``str``):
            Type of chat, can be either, "group", "supergroup" or "channel".

        members_count (``int``):
            Chat members count.

        photo (:obj:`~pylogram.types.Photo`, *optional*):
            Chat photo.

        members (List of :obj:`~pylogram.types.User`, *optional*):
            Preview of some of the chat members.
    """

    def __init__(
        self,
        *,
        client: "pylogram.Client" = None,
        title: str,
        type: str,
        members_count: int,
        photo: "types.Photo" = None,
        members: List["types.User"] = None,
        request_needed: bool = None,
        verified: bool = None,
        scam: bool = None,
        fake: bool = None,
        about: str = None
    ):
        super().__init__(client)

        self.title = title
        self.type = type
        self.members_count = members_count
        self.photo = photo
        self.members = members
        self.request_needed = request_needed
        self.verified = verified
        self.scam = scam
        self.fake = fake
        self.about = about

    @staticmethod
    def _parse(client, chat_invite: "raw.types.ChatInvite") -> "ChatPreview":
        return ChatPreview(
            title=chat_invite.title,
            type=("group" if not chat_invite.channel else
                  "channel" if chat_invite.broadcast else
                  "supergroup"),
            members_count=chat_invite.participants_count,
            photo=types.Photo._parse(client, chat_invite.photo),
            members=[types.User._parse(client, user) for user in chat_invite.participants] or None,
            client=client,
            request_needed=chat_invite.request_needed,
            verified=chat_invite.verified,
            scam=chat_invite.scam,
            fake=chat_invite.fake,
            about=chat_invite.about
        )

    # TODO: Maybe just merge this object into Chat itself by adding the "members" field.
    #  get_chat can be used as well instead of get_chat_preview
