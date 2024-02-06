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

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy

log = logging.getLogger(__name__)


class TCP:
    TIMEOUT = 10

    def __init__(self, ipv6: bool, proxy: dict):
        self.socket = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.proxy = self._parse_proxy(proxy) if proxy else None
        self.ipv6 = ipv6

    @staticmethod
    def _parse_proxy(proxy_data: Optional[dict]) -> Optional[Proxy]:
        if proxy_data is None:
            return None

        if not isinstance(proxy_data, dict):
            raise TypeError("Proxy must be a dict")

        scheme = proxy_data.get('scheme')
        hostname = proxy_data.get('hostname')
        port = proxy_data.get('port')
        rdns = proxy_data.get('rdns', True)
        username = proxy_data.get('username', None)
        password = proxy_data.get('password', None)

        if isinstance(scheme, str):
            scheme = scheme.lower()

        if scheme == ProxyType.SOCKS5 or scheme == 2 or scheme == "socks5":
            protocol = ProxyType.SOCKS5
        elif scheme == ProxyType.SOCKS4 or scheme == 1 or scheme == "socks4":
            protocol = ProxyType.SOCKS4
        elif scheme == ProxyType.HTTP or scheme == 3 or scheme == "http":
            protocol = ProxyType.HTTP
        else:
            raise ValueError("Unknown proxy protocol type: {}".format(scheme))

        return Proxy(protocol, hostname, port, username=username, password=password, rdns=rdns)

    async def connect(self, address: tuple):
        (ip_addr, port) = address

        if isinstance(self.proxy, Proxy):
            self.socket = await self.proxy.connect(dest_host=ip_addr, dest_port=port, timeout=TCP.TIMEOUT)
            log.info(f"Successfully connected to proxy {self.proxy.proxy_host}:{self.proxy.proxy_port}")
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(sock=self.socket),
                timeout=TCP.TIMEOUT,
            )
        else:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(host=ip_addr, port=port),
                timeout=TCP.TIMEOUT
            )

        await self.writer.drain()

    async def close(self):
        if self.writer is not None and not self.writer.is_closing():
            self.writer.close()
            try:
                await asyncio.wait_for(self.writer.wait_closed(), timeout=TCP.TIMEOUT)
            except (asyncio.TimeoutError, TimeoutError):
                log.warning('Graceful disconnection timed out, forcibly ignoring cleanup')
            except Exception as e:
                log.warning('%s during disconnect: %s', type(e).__name__, e)

    async def send(self, data: bytes):
        async with self.lock:
            try:
                if self.writer is not None:
                    self.writer.write(data)
                    await self.writer.drain()
            except Exception as e:
                log.info("Send exception: %s %s", type(e).__name__, e)
                raise OSError(e) from e

    async def recv(self, length: int = 0) -> Optional[bytes]:
        data = b""

        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(self.reader.read(length - len(data)), TCP.TIMEOUT)
            except (OSError, asyncio.TimeoutError, TimeoutError):
                return None
            else:
                if chunk:
                    data += chunk
                else:
                    return None

        return data
