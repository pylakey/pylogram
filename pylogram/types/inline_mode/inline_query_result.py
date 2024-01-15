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

from uuid import uuid4

import pylogram
from pylogram import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~pylogram.types.InlineQueryResultCachedAudio`
    - :obj:`~pylogram.types.InlineQueryResultCachedDocument`
    - :obj:`~pylogram.types.InlineQueryResultCachedAnimation`
    - :obj:`~pylogram.types.InlineQueryResultCachedPhoto`
    - :obj:`~pylogram.types.InlineQueryResultCachedSticker`
    - :obj:`~pylogram.types.InlineQueryResultCachedVideo`
    - :obj:`~pylogram.types.InlineQueryResultCachedVoice`
    - :obj:`~pylogram.types.InlineQueryResultArticle`
    - :obj:`~pylogram.types.InlineQueryResultAudio`
    - :obj:`~pylogram.types.InlineQueryResultContact`
    - :obj:`~pylogram.types.InlineQueryResultDocument`
    - :obj:`~pylogram.types.InlineQueryResultAnimation`
    - :obj:`~pylogram.types.InlineQueryResultLocation`
    - :obj:`~pylogram.types.InlineQueryResultPhoto`
    - :obj:`~pylogram.types.InlineQueryResultVenue`
    - :obj:`~pylogram.types.InlineQueryResultVideo`
    - :obj:`~pylogram.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "pylogram.Client"):
        pass
