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
import typing

from pylogram import enums
from pylogram import raw
from ..object import Object

sent_code_descriptions = {
    enums.SentCodeType.APP: "Telegram app",
    enums.SentCodeType.SMS: "SMS",
    enums.SentCodeType.CALL: "phone call",
    enums.SentCodeType.FLASH_CALL: "phone flash call",
    enums.SentCodeType.FRAGMENT_SMS: "Fragment SMS",
    enums.SentCodeType.EMAIL_CODE: "email code",
    enums.SentCodeType.MISSED_CALL: "phone missed call",
    enums.SentCodeType.SETUP_EMAIL_REQUIRED: "Email required to protect account",
}


class SentCode(Object):
    """Contains info on a sent confirmation code.

    Parameters:
        type (:obj:`~pylogram.enums.SentCodeType`):
            Type of the current sent code.

        phone_code_hash (``str``):
            Confirmation code identifier useful for the next authorization steps (either
            :meth:`~pylogram.Client.sign_in` or :meth:`~pylogram.Client.sign_up`).

        next_type (:obj:`~pylogram.enums.NextCodeType`, *optional*):
            Type of the next code to be sent with :meth:`~pylogram.Client.resend_code`.

        timeout (``int``, *optional*):
            Delay in seconds before calling :meth:`~pylogram.Client.resend_code`.
    """

    def __init__(
            self, *,
            type: "enums.SentCodeType",
            phone_code_hash: str,
            next_type: "enums.NextCodeType" = None,
            timeout: int = None
    ):
        super().__init__()

        self.type = type
        self.phone_code_hash = phone_code_hash
        self.next_type = next_type
        self.timeout = timeout

    @staticmethod
    def _parse(sent_code: raw.types.auth.SentCode) -> "SentCode":
        return SentCode(
            type=enums.SentCodeType(type(sent_code.type)),
            phone_code_hash=sent_code.phone_code_hash,
            next_type=enums.NextCodeType(type(sent_code.next_type)) if sent_code.next_type else None,
            timeout=sent_code.timeout
        )

    @property
    def description(self) -> typing.Optional[str]:
        return sent_code_descriptions.get(self.type)
