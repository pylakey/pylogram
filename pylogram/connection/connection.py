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

import asyncio
import logging
from typing import Optional
from typing import Type

from .transport import TCP
from .transport import TCPFull
from ..session.internals import DataCenter

log = logging.getLogger(__name__)


class Connection:
    MAX_CONNECTION_ATTEMPTS = 3

    def __init__(
            self,
            dc_id: int,
            test_mode: bool,
            ipv6: bool,
            proxy: dict,
            media: bool = False,
            protocol_class: Type[TCP] = TCPFull
    ):
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.ipv6 = ipv6
        self.proxy = proxy
        self.media = media
        self.address = DataCenter(dc_id, test_mode, ipv6, media)
        self.protocol_class = protocol_class
        self.protocol: TCP = None

    async def connect(self):
        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            self.protocol = self.protocol_class(self.ipv6, self.proxy)

            try:
                log.info(f"[%s] Connecting using protocol...", self.protocol_class.__name__)
                await self.protocol.connect(self.address)
            except OSError as e:
                log.warning("[%s] Unable to connect due to network issues: %s", self.protocol_class.__name__, e)
                await self.protocol.close()
                await asyncio.sleep(1)
            else:
                log.info(
                    "[%s] Connected! %s DC%s%s - IPv%s",
                    self.protocol_class.__name__,
                    "Test" if self.test_mode else "Production",
                    self.dc_id,
                    " (media)" if self.media else "",
                    "6" if self.ipv6 else "4"
                )
                break
        else:
            log.warning("[%s] Connection failed! Trying again...", self.protocol_class.__name__)
            raise ConnectionError

    async def close(self):
        await self.protocol.close()
        log.info("[%s] Disconnected", self.protocol_class.__name__)

    async def send(self, data: bytes):
        await self.protocol.send(data)

    async def recv(self) -> Optional[bytes]:
        return await self.protocol.recv()
