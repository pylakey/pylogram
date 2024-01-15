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

from typing import Optional, List

import pylogram
from pylogram import raw, types
from ..object import Object


class MessageReactions(Object):
    """Contains information about a message reactions.

    Parameters:
        reactions (List of :obj:`~pylogram.types.Reaction`):
            Reactions list.
    """

    def __init__(
        self,
        *,
        client: "pylogram.Client" = None,
        reactions: Optional[List["types.Reaction"]] = None,
    ):
        super().__init__(client)

        self.reactions = reactions

    @staticmethod
    def _parse(
        client: "pylogram.Client",
        message_reactions: Optional["raw.base.MessageReactions"] = None
    ) -> Optional["MessageReactions"]:
        if not message_reactions:
            return None

        return MessageReactions(
            client=client,
            reactions=[types.Reaction._parse_count(client, reaction)
                       for reaction in message_reactions.results]
        )
