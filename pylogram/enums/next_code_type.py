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

from pylogram import raw
from .auto_name import AutoName


class NextCodeType(AutoName):
    """Next code type enumeration used in :obj:`~pylogram.types.SentCode`."""

    CALL = raw.types.auth.CodeTypeCall
    "The code will be sent via a phone call. A synthesized voice will tell the user which verification code to input."

    FLASH_CALL = raw.types.auth.CodeTypeFlashCall
    "The code will be sent via a flash phone call, that will be closed immediately."

    MISSED_CALL = raw.types.auth.CodeTypeMissedCall
    "Missed call."

    SMS = raw.types.auth.CodeTypeSms
    "The code was sent via SMS."

    EMAIL_CODE = raw.types.auth.SentCodeTypeEmailCode
    "The code was sent via email."

    FRAGMENT_SMS = raw.types.auth.CodeTypeFragmentSms
    "The code was sent via Fragment SMS."
