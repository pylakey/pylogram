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

from ..object import Object

"""- :obj:`~pylogram.types.InputLocationMessageContent`
    - :obj:`~pylogram.types.InputVenueMessageContent`
    - :obj:`~pylogram.types.InputContactMessageContent`"""


class InputMessageContent(Object):
    """Content of a message to be sent as a result of an inline query.

    Pylogram currently supports the following types:

    - :obj:`~pylogram.types.InputTextMessageContent`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: "pylogram.Client", reply_markup):
        raise NotImplementedError
