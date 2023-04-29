#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.
from typing import Optional

from pyrogram import raw
from ..object import Object


class Username(Object):
    """
    User username info

    Parameters:
        username (``str``):
            N/A

        editable (``bool``, *optional*):
            N/A

        active (``bool``, *optional*):
            N/A
    """

    def __init__(self, *, username: str, editable: Optional[bool] = None, active: Optional[bool] = None) -> None:
        super().__init__(None)
        self.username = username
        self.editable = editable
        self.active = active

    @staticmethod
    def _parse(username: "raw.types.Username") -> "Username":
        return Username(
            username=username.username,
            editable=username.editable,
            active=username.active
        )
