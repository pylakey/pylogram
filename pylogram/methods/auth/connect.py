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
from pylogram.session import Session


class Connect:
    async def connect(
        self: "pylogram.Client",
    ) -> bool:
        """
        Connect the client to Telegram servers.

        Returns:
            ``bool``: On success, in case the passed-in session is authorized, True is returned. Otherwise, in case
            the session needs to be authorized, False is returned.

        Raises:
            ConnectionError: In case you try to connect an already connected client.
        """
        if self.is_connected:
            raise ConnectionError("Client is already connected")

        await self.load_session()

        self.session = Session(
            self,
            await self.storage.dc_id(),
            await self.storage.auth_key(),
            await self.storage.test_mode(),
            is_media=False,
            is_cdn=False,
            connection_protocol_class=self.connection_protocol_class,
        )

        await self.session.start()
        self._build_invoker()

        # Start UpdatesManager for gap recovery (if not disabled)
        if not self.no_updates:
            cfg = self._updates_config
            if cfg is None or cfg.enabled:
                await self._start_updates_manager()

        self.is_connected = True

        return bool(await self.storage.user_id())

    async def _start_updates_manager(self: "pylogram.Client") -> None:
        from pylogram.updates import UpdatesManager, UpdatesConfig
        from pylogram import utils as _utils

        if self._updates_config is None:
            storage = self.storage
            dispatcher = self.dispatcher

            async def _get_peer(peer_id: int):
                try:
                    return await storage.get_peer_by_id(peer_id)
                except KeyError:
                    return None

            async def _get_channel_access_hash(channel_id: int):
                try:
                    peer = await storage.get_peer_by_id(_utils.get_channel_id(channel_id))
                    return getattr(peer, "access_hash", None)
                except KeyError:
                    return None

            self._updates_config = UpdatesConfig(
                on_update=lambda u, users, chats: dispatcher.updates_queue.put_nowait(
                    (u, users, chats)
                ),
                on_peers=self.update_storage_peers_both,
                invoke=self._invoker,
                get_channel_access_hash=_get_channel_access_hash,
                get_peer=_get_peer,
                get_my_user_id=storage.user_id,
                get_state=storage.get_update_state,
                set_state=storage.set_update_state,
                get_channel_pts=storage.get_channel_pts,
                set_channel_pts=storage.set_channel_pts,
                is_bot=bool(await storage.is_bot()),
            )

        self._updates_manager = UpdatesManager(self._updates_config)
        await self._updates_manager.start()
