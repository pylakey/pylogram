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
from pylogram import raw


class UpdateProfile:
    async def update_profile(
        self: "pylogram.Client",
        first_name: str = None,
        last_name: str = None,
        bio: str = None
    ) -> bool:
        """Update your profile details such as first name, last name and bio.

        You can omit the parameters you don't want to change.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            first_name (``str``, *optional*):
                The new first name.

            last_name (``str``, *optional*):
                The new last name.
                Pass "" (empty string) to remove it.

            bio (``str``, *optional*):
                The new bio, also known as "about". Max 70 characters.
                Pass "" (empty string) to remove it.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Update your first name only
                await app.update_profile(first_name="Pylogram")

                # Update first name and bio
                await app.update_profile(first_name="Pylogram", bio="https://example.com/")

                # Remove the last name
                await app.update_profile(last_name="")
        """

        return bool(
            await self.invoke(
                raw.functions.account.UpdateProfile(
                    first_name=first_name,
                    last_name=last_name,
                    about=bio
                )
            )
        )
