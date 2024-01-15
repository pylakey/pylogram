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

import logging

import pylogram
from pylogram import raw
from pylogram import types
from pylogram.utils import compute_password_check

log = logging.getLogger(__name__)


class CheckPassword:
    async def check_password(
            self: "pylogram.Client",
            password: str,
            *,
            password_info: raw.types.account.Password = None
    ) -> "types.User":
        """Check your Two-Step Verification password and log in.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            password_info ():
            password (``str``):
                Your Two-Step Verification password.

        Returns:
            :obj:`~pylogram.types.User`: On success, the authorized user is returned.

        Raises:
            BadRequest: In case the password is invalid.
        """

        if not isinstance(password_info, raw.types.account.Password):
            password_info = await self.invoke(raw.functions.account.GetPassword())

        r = await self.invoke(
            raw.functions.auth.CheckPassword(
                password=compute_password_check(password_info, password)
            )
        )

        await self.storage.user_id(r.user.id)
        await self.storage.is_bot(False)

        return types.User._parse(self, r.user)
