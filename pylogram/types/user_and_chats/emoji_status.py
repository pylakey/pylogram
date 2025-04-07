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

from datetime import datetime
from typing import Optional

import pylogram
from pylogram import raw, utils

from ..object import Object


class EmojiStatus(Object):
    """A user emoji status.

    Parameters:
        custom_emoji_id (``int``):
            Custom emoji id.

        until_date (:py:obj:`~datetime.datetime`, *optional*):
            Valid until date.
    """

    def __init__(
        self,
        *,
        client: "pylogram.Client" = None,
        # Custom emoji status
        custom_emoji_id: Optional[int] = None,
        until_date: Optional[datetime] = None,
        # Collectible status
        collectible_id: Optional[int] = None,
        title: Optional[str] = None,
        slug: Optional[str] = None,
        pattern_document_id: Optional[int] = None,
        center_color: Optional[int] = None,
        edge_color: Optional[int] = None,
        pattern_color: Optional[int] = None,
        text_color: Optional[int] = None,
    ):
        super().__init__(client)

        self.until_date = until_date

        # Custom emoji status
        self.custom_emoji_id = custom_emoji_id
        # Collectible status
        self.collectible_id = collectible_id
        self.title = title
        self.slug = slug
        self.pattern_document_id = pattern_document_id
        self.center_color = center_color
        self.edge_color = edge_color
        self.pattern_color = pattern_color
        self.text_color = text_color

    @staticmethod
    def _parse(client, emoji_status: "raw.base.EmojiStatus") -> Optional["EmojiStatus"]:
        if isinstance(emoji_status, raw.types.EmojiStatus):
            return EmojiStatus(
                client=client,
                custom_emoji_id=emoji_status.document_id,
                until_date=utils.timestamp_to_datetime(emoji_status.until),
            )

        if isinstance(emoji_status, raw.types.EmojiStatusCollectible):
            return EmojiStatus(
                client=client,
                custom_emoji_id=emoji_status.document_id,
                until_date=utils.timestamp_to_datetime(emoji_status.until),
                collectible_id=emoji_status.collectible_id,
                title=emoji_status.title,
                slug=emoji_status.slug,
                pattern_document_id=emoji_status.pattern_document_id,
                center_color=emoji_status.center_color,
                edge_color=emoji_status.edge_color,
                pattern_color=emoji_status.pattern_color,
                text_color=emoji_status.text_color,
            )

        return None

    def write(self):
        if self.collectible_id:
            return raw.types.EmojiStatusCollectible(
                collectible_id=self.collectible_id,
                document_id=self.custom_emoji_id,
                until=utils.datetime_to_timestamp(self.until_date),
                title=self.title,
                slug=self.slug,
                pattern_document_id=self.pattern_document_id,
                center_color=self.center_color,
                edge_color=self.edge_color,
                pattern_color=self.pattern_color,
                text_color=self.text_color,
            )

        if self.custom_emoji_id:
            return raw.types.EmojiStatus(
                document_id=self.custom_emoji_id,
                until=utils.datetime_to_timestamp(self.until_date),
            )

        return raw.types.EmojiStatusEmpty()
