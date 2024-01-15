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

import tgcrypto

log = logging.getLogger(__name__)


def ige256_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return tgcrypto.ige256_encrypt(data, key, iv)


def ige256_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return tgcrypto.ige256_decrypt(data, key, iv)


def ctr256_encrypt(data: bytes, key: bytes, iv: bytearray, state: bytearray = None) -> bytes:
    return tgcrypto.ctr256_encrypt(data, key, iv, state or bytearray(1))


def ctr256_decrypt(data: bytes, key: bytes, iv: bytearray, state: bytearray = None) -> bytes:
    return tgcrypto.ctr256_decrypt(data, key, iv, state or bytearray(1))


def xor(a: bytes, b: bytes) -> bytes:
    return int.to_bytes(
        int.from_bytes(a, "big") ^ int.from_bytes(b, "big"),
        len(a),
        "big",
    )
