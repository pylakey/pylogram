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
import functools
import inspect
import logging
import os
import platform
import re
import shutil
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from hashlib import sha256
from importlib import import_module
from io import BytesIO, StringIO
from mimetypes import MimeTypes
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Type, Union

import pylogram
import pylogram.errors.lib_errors
from pylogram import __version__, enums, raw, typevars, utils
from pylogram.connection.transport import TCP, TCPFull
from pylogram.crypto import aes
from pylogram.dispatcher import Dispatcher
from pylogram.errors import (
    CDNFileHashMismatch,
    ChannelPrivate,
    SessionPasswordNeeded,
    VolumeLocNotFound,
)
from pylogram.file_id import FileId, FileType, ThumbnailSource
from pylogram.handlers.handler import Handler
from pylogram.methods import Methods
from pylogram.mime_types import mime_types
from pylogram.parser import Parser
from pylogram.session import Auth, Session
from pylogram.session.internals import MsgId
from pylogram.storage import FileStorage, MemoryStorage, Storage
from pylogram.types import Dialog, TermsOfService, User
from pylogram.utils import ainput

log = logging.getLogger(__name__)


class Client(Methods):
    """Pylogram Client, the main means for interacting with Telegram.

    Parameters:
        session_name (``str``):
            A name for the client, e.g.: "my_account".

        api_id (``int`` | ``str``, *optional*):
            The *api_id* part of the Telegram API key, as integer or string.
            E.g.: 12345 or "12345".

        api_hash (``str``, *optional*):
            The *api_hash* part of the Telegram API key, as string.
            E.g.: "0123456789abcdef0123456789abcdef".

        app_version (``str``, *optional*):
            Application version.
            Defaults to "Pylogram x.y.z".

        device_model (``str``, *optional*):
            Device model.
            Defaults to *platform.python_implementation() + " " + platform.python_version()*.

        system_version (``str``, *optional*):
            Operating System version.
            Defaults to *platform.system() + " " + platform.release()*.

        lang_code (``str``, *optional*):
            Code of the language used on the client, in ISO 639-1 standard.
            Defaults to "en".

        ipv6 (``bool``, *optional*):
            Pass True to connect to Telegram using IPv6.
            Defaults to False (IPv4).

        proxy (``dict``, *optional*):
            The Proxy settings as dict.
            E.g.: *dict(scheme="socks5", hostname="11.22.33.44", port=1234, username="user", password="pass")*.
            The *username* and *password* can be omitted if the proxy doesn't require authorization.

        test_mode (``bool``, *optional*):
            Enable or disable login to the test servers.
            Only applicable for new sessions and will be ignored in case previously created sessions are loaded.
            Defaults to False.

        bot_token (``str``, *optional*):
            Pass the Bot API token to create a bot session, e.g.: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            Only applicable for new sessions.

        session_string (``str``, *optional*):
            Pass a session string to load the session in-memory.
            Implies ``in_memory=True``.

        in_memory (``bool``, *optional*):
            Pass True to start an in-memory session that will be discarded as soon as the client stops.
            In order to reconnect again using an in-memory session without having to login again, you can use
            :meth:`~pylogram.Client.export_session_string` before stopping the client to get a session string you can
            pass to the ``session_string`` parameter.
            Defaults to False.

        phone_number (``str``, *optional*):
            Pass the phone number as string (with the Country Code prefix included) to avoid entering it manually.
            Only applicable for new sessions.

        phone_code (``str``, *optional*):
            Pass the phone code as string (for test numbers only) to avoid entering it manually.
            Only applicable for new sessions.

        password (``str``, *optional*):
            Pass the Two-Step Verification password as string (if required) to avoid entering it manually.
            Only applicable for new sessions.

        workers (``int``, *optional*):
            Number of maximum concurrent workers for handling incoming updates.
            Defaults to ``min(32, os.cpu_count() + 4)``.

        workdir (``str``, *optional*):
            Define a custom working directory.
            The working directory is the location in the filesystem where Pylogram will store the session files.
            Defaults to the parent directory of the main script.

        plugins (``dict``, *optional*):
            Smart Plugins settings as dict, e.g.: *dict(root="plugins")*.

        parse_mode (:obj:`~pylogram.enums.ParseMode`, *optional*):
            Set the global parse mode of the client. By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        no_updates (``bool``, *optional*):
            Pass True to disable incoming updates.
            When updates are disabled the client can't receive messages or other updates.
            Useful for batch programs that don't need to deal with updates.
            Defaults to False (updates enabled and received).

        takeout (``bool``, *optional*):
            Pass True to let the client use a takeout session instead of a normal one, implies *no_updates=True*.
            Useful for exporting Telegram data. Methods invoked inside a takeout session (such as get_chat_history,
            download_media, ...) are less prone to throw FloodWait exceptions.
            Only available for users, bots will ignore this parameter.
            Defaults to False (normal session).

        sleep_threshold (``int``, *optional*):
            Set a sleep threshold for flood wait exceptions happening globally in this client instance, below which any
            request that raises a flood wait will be automatically invoked again after sleeping for the required amount
            of time. Flood wait exceptions requiring higher waiting times will be raised.
            Defaults to 10 seconds.

        hide_password (``bool``, *optional*):
            Pass True to hide the password when typing it during the login.
            Defaults to False, because ``getpass`` (the library used) is known to be problematic in some
            terminal environments.

        max_concurrent_transmissions (``bool``, *optional*):
            Set the maximum amount of concurrent transmissions (uploads & downloads).
            A value that is too high may result in network related issues.
            Defaults to 1.
    """

    APP_VERSION = f"{__version__}"
    DEVICE_MODEL = f"{platform.python_implementation()} {platform.python_version()}"
    SYSTEM_VERSION = f"{platform.system()} {platform.release()}"
    LANG_CODE = "en"
    SYSTEM_LANG_CODE = "en-US"
    PARENT_DIR = Path.cwd().parent
    INVITE_LINK_RE = re.compile(
        r"^(?:https?://)?(?:www\.)?t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+)([\w-]+)$"
    )
    WORKERS = min(8, (os.cpu_count() or 0) + 4)  # os.cpu_count() can be None
    DEFAULT_WORKDIR = PARENT_DIR
    # Interval of seconds in which the updates watchdog will kick in
    UPDATES_WATCHDOG_INTERVAL = 5 * 60
    MAX_CONCURRENT_TRANSMISSIONS = 1

    mimetypes = MimeTypes()
    mimetypes.readfp(StringIO(mime_types))

    def __init__(
        self,
        session_name: str,
        *,
        session_storage: Optional[Storage] = None,
        api_id: Union[int, str] = None,
        api_hash: str = None,
        app_version: str = APP_VERSION,
        device_model: str = DEVICE_MODEL,
        system_version: str = SYSTEM_VERSION,
        system_lang_code: str = SYSTEM_LANG_CODE,
        lang_code: str = LANG_CODE,
        lang_pack: str = "",
        ipv6: bool = False,
        proxy: dict = None,
        test_mode: bool = False,
        bot_token: str = None,
        session_string: str = None,
        in_memory: bool = None,
        phone_number: str = None,
        phone_code: str = None,
        password: str = None,
        workers: int = WORKERS,
        workdir: str = DEFAULT_WORKDIR,
        plugins: dict = None,
        parse_mode: "enums.ParseMode" = enums.ParseMode.HTML,
        no_updates: bool = None,
        takeout: bool = None,
        sleep_threshold: int = Session.SLEEP_THRESHOLD,
        hide_password: bool = False,
        max_concurrent_transmissions: int = MAX_CONCURRENT_TRANSMISSIONS,
        ignore_channel_updates_except: List[int] = None,
        message_cache_size: int = 10000,
        first_name: str = None,
        last_name: str = None,
        connection_protocol_class: Type[TCP] = TCPFull,
        commit_storage_peers_on_update: bool = False,
    ):
        super().__init__()

        self.session_name = session_name
        self.api_id = int(api_id) if api_id else None
        self.api_hash = api_hash
        self.app_version = app_version
        self.device_model = device_model
        self.system_version = system_version
        self.system_lang_code = system_lang_code
        self.lang_code = lang_code
        self.lang_pack = lang_pack
        self.ipv6 = ipv6
        self.proxy = proxy
        self.test_mode = test_mode
        self.bot_token = bot_token
        self.session_string = session_string
        self.in_memory = in_memory
        self.phone_number = phone_number
        self.phone_code = phone_code
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.workers = workers
        self.workdir = Path(workdir)
        self.plugins = plugins
        self.parse_mode = parse_mode
        self.no_updates = no_updates
        self.takeout = takeout
        self.sleep_threshold = sleep_threshold
        self.hide_password = hide_password
        self.max_concurrent_transmissions = max_concurrent_transmissions
        self.executor = ThreadPoolExecutor(self.workers, thread_name_prefix="Handler")
        self.connection_protocol_class = connection_protocol_class
        self.commit_storage_peers_on_update = commit_storage_peers_on_update

        if isinstance(session_storage, Storage):
            self.storage = session_storage
        else:
            if self.session_string:
                self.storage = MemoryStorage(self.session_name, self.session_string)
            elif self.in_memory:
                self.storage = MemoryStorage(self.session_name)
            else:
                self.storage = FileStorage(self.session_name, self.workdir)

        self.dispatcher = Dispatcher(self)
        self.rnd_id = MsgId
        self.parser = Parser(self)
        self.session = None
        self.media_sessions = {}
        self.media_sessions_lock = asyncio.Lock()
        self.save_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)
        self.get_file_semaphore = asyncio.Semaphore(self.max_concurrent_transmissions)
        self.is_connected = None
        self.is_initialized = None
        self.takeout_id = None
        self.disconnect_handler = None
        self.me: Optional[User] = None
        self.message_cache = Cache(message_cache_size)

        # Sometimes, for some reason, the server will stop sending updates and will only respond to pings.
        # This watchdog will invoke updates.GetState in order to wake up the server and enable it sending updates again
        # after some idle time has been detected.
        self.updates_watchdog_task = None
        self.updates_watchdog_event = asyncio.Event()
        self.last_update_time = datetime.now()
        self.ignore_channel_updates_except = ignore_channel_updates_except
        self.dialogs: List[Dialog] = []
        self.dialogs_lock: asyncio.Lock = asyncio.Lock()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        try:
            self.stop()
        except ConnectionError:
            pass

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        try:
            await self.stop()
        except ConnectionError:
            pass

    async def updates_watchdog(self):
        while True:
            try:
                await asyncio.wait_for(
                    self.updates_watchdog_event.wait(), self.UPDATES_WATCHDOG_INTERVAL
                )
            except (asyncio.TimeoutError, TimeoutError):
                pass
            else:
                break

            if datetime.now() - self.last_update_time > timedelta(
                seconds=self.UPDATES_WATCHDOG_INTERVAL
            ):
                await self.invoke(raw.functions.updates.GetState())

    async def fetch_phone_number(self) -> str:
        phone_number = self.phone_number

        if not bool(phone_number):
            phone_number = await ainput("Enter phone number: ")

        if not bool(phone_number):
            raise RuntimeError(
                "The phone number or bot token required for new authorizations"
            )

        phone_number = re.sub(r"\D", "", phone_number)

        return phone_number

    async def fetch_phone_code(
        self,
        *,
        sent_code: Optional[raw.types.auth.SentCode] = None,
    ) -> str:
        phone_code = self.phone_code

        if not bool(phone_code):
            if isinstance(sent_code, raw.types.auth.SentCode):
                if isinstance(sent_code.type, raw.types.auth.SentCodeTypeApp):
                    hint = "Enter confirmation code from the app: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeSms):
                    hint = "Enter confirmation code from the SMS: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeCall):
                    hint = "Enter confirmation code from the call: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeEmailCode):
                    hint = f"Enter confirmation code from the email {sent_code.type.email_pattern}: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeFirebaseSms):
                    hint = "Enter confirmation code from the Firebase SMS: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeFlashCall):
                    hint = f"Enter confirmation code from the flash call {sent_code.type.pattern}: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeFragmentSms):
                    hint = f"Enter confirmation code from the Fragment SMS {sent_code.type.url}: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeMissedCall):
                    hint = "Enter confirmation code from the missed call: "
                elif isinstance(
                    sent_code.type, raw.types.auth.SentCodeTypeSetUpEmailRequired
                ):
                    raise RuntimeError(
                        "Email is required to continue authorization process"
                    )
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeSmsPhrase):
                    hint = f"Enter confirmation code from the SMS phrase {sent_code.type.beginning}: "
                elif isinstance(sent_code.type, raw.types.auth.SentCodeTypeSmsWord):
                    hint = f"Enter confirmation code from the SMS word {sent_code.type.beginning}: "
            else:
                hint = f"Enter confirmation code (Unknown method - {sent_code.__class__.__name__}): "

            phone_code = await ainput(hint)

        if not bool(phone_code):
            raise RuntimeError("The auth code required for signing in")

        phone_code = re.sub(r"\D", "", phone_code)

        return phone_code

    async def fetch_password(self, hint: str = None) -> str:
        password = self.password

        if not bool(password):
            password = await ainput(
                f"Enter password (empty to recover). Hint: {hint}: ",
                hide=self.hide_password,
            )

        return password

    async def fetch_first_name(self) -> str:
        first_name = self.first_name

        if not bool(first_name):
            first_name = await ainput("Enter first name: ")

        if not bool(first_name):
            raise RuntimeError("The first name required for new authorizations")

        return first_name

    async def fetch_last_name(self) -> str:
        last_name = self.last_name

        if not bool(last_name):
            last_name = await ainput("Enter first name: ")

        return last_name

    async def authorize(self) -> User:
        if self.bot_token:
            return await self.sign_in_bot(self.bot_token)

        phone_number = await self.fetch_phone_number()
        sent_code = await self.send_code(phone_number)
        log.debug(
            f"The confirmation code for {phone_number} has been sent via {sent_code.description}"
        )
        phone_code = await self.fetch_phone_code(sent_code=sent_code.get_raw())

        try:
            signed_in = await self.sign_in(
                phone_number,
                sent_code.phone_code_hash,
                phone_code,
            )
        except SessionPasswordNeeded as e:
            log.info(e.MESSAGE)
            password_info = await self.invoke(raw.functions.account.GetPassword())
            password = await self.fetch_password(password_info.hint)

            if not bool(password):
                raise

            return await self.check_password(password, password_info=password_info)

        if isinstance(signed_in, User):
            return signed_in

        first_name = await self.fetch_first_name()
        last_name = await self.fetch_last_name()
        signed_up = await self.sign_up(
            self.phone_number, sent_code.phone_code_hash, first_name, last_name or ""
        )

        if isinstance(signed_in, TermsOfService):
            print("\n" + signed_in.text + "\n")
            await self.accept_terms_of_service(signed_in.id)

        return signed_up

    def set_parse_mode(self, parse_mode: Optional["enums.ParseMode"]):
        """Set the parse mode to be used globally by the client.

        When setting the parse mode with this method, all other methods having a *parse_mode* parameter will follow the
        global value by default.

        Parameters:
            parse_mode (:obj:`~pylogram.enums.ParseMode`):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

        Example:
            .. code-block:: python

                from pylogram import enums

                # Default combined mode: Markdown + HTML
                await app.send_message("me", "1. **markdown** and <i>html</i>")

                # Force Markdown-only, HTML is disabled
                app.set_parse_mode(enums.ParseMode.MARKDOWN)
                await app.send_message("me", "2. **markdown** and <i>html</i>")

                # Force HTML-only, Markdown is disabled
                app.set_parse_mode(enums.ParseMode.HTML)
                await app.send_message("me", "3. **markdown** and <i>html</i>")

                # Disable the parser completely
                app.set_parse_mode(enums.ParseMode.DISABLED)
                await app.send_message("me", "4. **markdown** and <i>html</i>")

                # Bring back the default combined mode
                app.set_parse_mode(enums.ParseMode.DEFAULT)
                await app.send_message("me", "5. **markdown** and <i>html</i>")
        """

        self.parse_mode = parse_mode

    async def update_storage_peers(
        self,
        peers: List[Union[raw.base.User, raw.base.Chat]],
    ) -> bool:
        is_min = False
        parsed_peers = []

        for peer in peers:
            if getattr(peer, "min", False):
                is_min = True
                continue

            username = None
            phone_number = None

            if isinstance(peer, raw.types.User):
                peer_id = peer.id
                access_hash = peer.access_hash
                username = (
                    peer.username.lower()
                    if peer.username
                    else peer.usernames[0].username.lower()
                    if peer.usernames
                    else None
                )
                phone_number = peer.phone
                peer_type = "bot" if peer.bot else "user"
            elif isinstance(peer, raw.types.UserEmpty):
                continue
            elif isinstance(peer, raw.types.Channel):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                username = (
                    peer.username.lower()
                    if peer.username
                    else peer.usernames[0].username.lower()
                    if peer.usernames
                    else None
                )
                peer_type = "channel" if peer.broadcast else "supergroup"
            elif isinstance(peer, raw.types.ChannelForbidden):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"
            elif isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                peer_id = -peer.id
                access_hash = 0
                peer_type = "group"
            elif isinstance(peer, raw.types.ChatEmpty):
                continue
            else:
                continue

            parsed_peers.append(
                (peer_id, access_hash, peer_type, username, phone_number)
            )

        await self.storage.update_peers(parsed_peers)

        if self.commit_storage_peers_on_update:
            await self.storage.save()

        return is_min

    async def handle_updates(self, updates):
        self.last_update_time = datetime.now()

        if isinstance(updates, (raw.types.Updates, raw.types.UpdatesCombined)):
            is_min = any(
                (
                    await self.update_storage_peers(updates.users),
                    await self.update_storage_peers(updates.chats),
                )
            )

            users = {u.id: u for u in updates.users}
            chats = {c.id: c for c in updates.chats}

            for update in updates.updates:
                channel_id = getattr(
                    getattr(getattr(update, "message", None), "peer_id", None),
                    "channel_id",
                    None,
                ) or getattr(update, "channel_id", None)

                pts = getattr(update, "pts", None)
                pts_count = getattr(update, "pts_count", None)

                if isinstance(update, raw.types.UpdateChannelTooLong):
                    log.info(update)

                if isinstance(update, raw.types.UpdateNewChannelMessage) and is_min:
                    message = update.message

                    if (
                        bool(self.ignore_channel_updates_except)
                        and utils.get_channel_id(channel_id)
                        not in self.ignore_channel_updates_except
                    ):
                        continue

                    if not isinstance(message, raw.types.MessageEmpty):
                        try:
                            diff = await self.invoke(
                                raw.functions.updates.GetChannelDifference(
                                    channel=await self.resolve_peer(
                                        utils.get_channel_id(channel_id)
                                    ),
                                    filter=raw.types.ChannelMessagesFilter(
                                        ranges=[
                                            raw.types.MessageRange(
                                                min_id=update.message.id,
                                                max_id=update.message.id,
                                            )
                                        ]
                                    ),
                                    pts=pts - pts_count,
                                    limit=pts,
                                )
                            )
                        except ChannelPrivate:
                            pass
                        else:
                            if not isinstance(
                                diff, raw.types.updates.ChannelDifferenceEmpty
                            ):
                                users.update({u.id: u for u in diff.users})
                                chats.update({c.id: c for c in diff.chats})

                self.dispatcher.updates_queue.put_nowait((update, users, chats))
        elif isinstance(
            updates, (raw.types.UpdateShortMessage, raw.types.UpdateShortChatMessage)
        ):
            diff = await self.invoke(
                raw.functions.updates.GetDifference(
                    pts=updates.pts - updates.pts_count, date=updates.date, qts=-1
                )
            )

            if diff.new_messages:
                self.dispatcher.updates_queue.put_nowait(
                    (
                        raw.types.UpdateNewMessage(
                            message=diff.new_messages[0],
                            pts=updates.pts,
                            pts_count=updates.pts_count,
                        ),
                        {u.id: u for u in diff.users},
                        {c.id: c for c in diff.chats},
                    )
                )
            else:
                if diff.other_updates:  # The other_updates list can be empty
                    self.dispatcher.updates_queue.put_nowait(
                        (diff.other_updates[0], {}, {})
                    )
        elif isinstance(updates, raw.types.UpdateShort):
            self.dispatcher.updates_queue.put_nowait((updates.update, {}, {}))
        elif isinstance(updates, raw.types.UpdatesTooLong):
            log.info(updates)

    async def load_session(self):
        await self.storage.open()

        session_empty = any(
            [
                await self.storage.test_mode() is None,
                await self.storage.auth_key() is None,
                await self.storage.user_id() is None,
                await self.storage.is_bot() is None,
            ]
        )

        if session_empty:
            if not self.api_id or not self.api_hash:
                raise AttributeError("The API key is required for new authorizations.")

            await self.storage.api_id(self.api_id)
            await self.storage.dc_id(2)
            await self.storage.date(0)
            await self.storage.test_mode(self.test_mode)
            await self.storage.auth_key(
                await Auth(
                    self,
                    await self.storage.dc_id(),
                    await self.storage.test_mode(),
                    connection_protocol_class=self.connection_protocol_class,
                ).create()
            )
            await self.storage.user_id(None)
            await self.storage.is_bot(None)
        else:
            if not await self.storage.api_id():
                await self.storage.api_id(self.api_id)

    def load_plugins(self):
        if self.plugins:
            plugins = self.plugins.copy()

            for option in ["include", "exclude"]:
                if plugins.get(option, []):
                    plugins[option] = [
                        (i.split()[0], i.split()[1:] or None)
                        for i in self.plugins[option]
                    ]
        else:
            return

        if plugins.get("enabled", True):
            root = plugins["root"]
            include = plugins.get("include", [])
            exclude = plugins.get("exclude", [])

            count = 0

            if not include:
                for path in sorted(Path(root.replace(".", "/")).rglob("*.py")):
                    module_path = ".".join(path.parent.parts + (path.stem,))
                    module = import_module(module_path)

                    for name in vars(module).keys():
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(
                                    group, int
                                ):
                                    self.add_handler(handler, group)

                                    log.info(
                                        '[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                            self.session_name,
                                            type(handler).__name__,
                                            name,
                                            group,
                                            module_path,
                                        )
                                    )

                                    count += 1
                        except Exception:
                            pass
            else:
                for path, handlers in include:
                    if not bool(root) or root == ".":
                        module_path = path
                    else:
                        module_path = root + "." + path

                    warn_non_existent_functions = True

                    try:
                        module = import_module(module_path)
                    except ImportError:
                        log.warning(
                            '[%s] [LOAD] Ignoring non-existent module "%s"',
                            self.session_name,
                            module_path,
                        )
                        continue

                    if "__path__" in dir(module):
                        log.warning(
                            '[%s] [LOAD] Ignoring namespace "%s"',
                            self.session_name,
                            module_path,
                        )
                        continue

                    if handlers is None:
                        handlers = vars(module).keys()
                        warn_non_existent_functions = False

                    for name in handlers:
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(
                                    group, int
                                ):
                                    self.add_handler(handler, group)

                                    log.info(
                                        '[{}] [LOAD] {}("{}") in group {} from "{}"'.format(
                                            self.session_name,
                                            type(handler).__name__,
                                            name,
                                            group,
                                            module_path,
                                        )
                                    )

                                    count += 1
                        except Exception:
                            if warn_non_existent_functions:
                                log.warning(
                                    '[{}] [LOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                        self.session_name, name, module_path
                                    )
                                )

            if exclude:
                for path, handlers in exclude:
                    if not bool(root) or root == ".":
                        module_path = path
                    else:
                        module_path = root + "." + path
                    warn_non_existent_functions = True

                    try:
                        module = import_module(module_path)
                    except ImportError:
                        log.warning(
                            '[%s] [UNLOAD] Ignoring non-existent module "%s"',
                            self.session_name,
                            module_path,
                        )
                        continue

                    if "__path__" in dir(module):
                        log.warning(
                            '[%s] [UNLOAD] Ignoring namespace "%s"',
                            self.session_name,
                            module_path,
                        )
                        continue

                    if handlers is None:
                        handlers = vars(module).keys()
                        warn_non_existent_functions = False

                    for name in handlers:
                        # noinspection PyBroadException
                        try:
                            for handler, group in getattr(module, name).handlers:
                                if isinstance(handler, Handler) and isinstance(
                                    group, int
                                ):
                                    self.remove_handler(handler, group)

                                    log.info(
                                        '[{}] [UNLOAD] {}("{}") from group {} in "{}"'.format(
                                            self.session_name,
                                            type(handler).__name__,
                                            name,
                                            group,
                                            module_path,
                                        )
                                    )

                                    count -= 1
                        except Exception:
                            if warn_non_existent_functions:
                                log.warning(
                                    '[{}] [UNLOAD] Ignoring non-existent function "{}" from "{}"'.format(
                                        self.session_name, name, module_path
                                    )
                                )

            if count > 0:
                log.info(
                    '[{}] Successfully loaded {} plugin{} from "{}"'.format(
                        self.session_name, count, "s" if count > 1 else "", root
                    )
                )
            else:
                log.warning('[%s] No plugin loaded from "%s"', self.session_name, root)

    async def handle_download(self, packet):
        file_id, directory, file_name, in_memory, file_size, progress, progress_args = (
            packet
        )

        os.makedirs(directory, exist_ok=True) if not in_memory else None
        temp_file_path = (
            os.path.abspath(re.sub("\\\\", "/", os.path.join(directory, file_name)))
            + ".temp"
        )
        file = BytesIO() if in_memory else open(temp_file_path, "wb")

        try:
            async for chunk in self.get_file(
                file_id, file_size, 0, 0, progress, progress_args
            ):
                file.write(chunk)
        except Exception as e:
            if not in_memory:
                file.close()
                os.remove(temp_file_path)

            if isinstance(e, asyncio.CancelledError):
                raise e

            return None
        else:
            if in_memory:
                file.name = file_name
                return file
            else:
                file.close()
                file_path = os.path.splitext(temp_file_path)[0]
                shutil.move(temp_file_path, file_path)
                return file_path

    async def get_file(
        self,
        file_id: FileId,
        file_size: int = 0,
        limit: int = 0,
        offset: int = 0,
        progress: typevars.ProgressCallable = None,
        progress_args: tuple = (),
    ) -> Optional[AsyncGenerator[bytes, None]]:
        async with self.get_file_semaphore:
            file_type = file_id.file_type

            if file_type == FileType.CHAT_PHOTO:
                if file_id.chat_id > 0:
                    peer = raw.types.InputPeerUser(
                        user_id=file_id.chat_id, access_hash=file_id.chat_access_hash
                    )
                else:
                    if file_id.chat_access_hash == 0:
                        peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
                    else:
                        peer = raw.types.InputPeerChannel(
                            channel_id=utils.get_channel_id(file_id.chat_id),
                            access_hash=file_id.chat_access_hash,
                        )

                location = raw.types.InputPeerPhotoFileLocation(
                    peer=peer,
                    photo_id=file_id.media_id,
                    big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
                )
            elif file_type == FileType.PHOTO:
                location = raw.types.InputPhotoFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size,
                )
            else:
                location = raw.types.InputDocumentFileLocation(
                    id=file_id.media_id,
                    access_hash=file_id.access_hash,
                    file_reference=file_id.file_reference,
                    thumb_size=file_id.thumbnail_size,
                )

            current = 0
            total = abs(limit) or (1 << 31) - 1
            chunk_size = 1024 * 1024
            offset_bytes = abs(offset) * chunk_size

            dc_id = file_id.dc_id
            auth_key = (
                await Auth(
                    self,
                    dc_id,
                    await self.storage.test_mode(),
                    connection_protocol_class=self.connection_protocol_class,
                ).create()
                if dc_id != await self.storage.dc_id()
                else await self.storage.auth_key()
            )
            session = Session(
                self,
                dc_id,
                auth_key,
                await self.storage.test_mode(),
                is_media=True,
                connection_protocol_class=self.connection_protocol_class,
            )

            try:
                await session.start()

                if dc_id != await self.storage.dc_id():
                    exported_auth = await self.invoke(
                        raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                    )

                    await session.invoke(
                        raw.functions.auth.ImportAuthorization(
                            id=exported_auth.id, bytes=exported_auth.bytes
                        )
                    )

                r = await session.invoke(
                    raw.functions.upload.GetFile(
                        location=location, offset=offset_bytes, limit=chunk_size
                    ),
                    sleep_threshold=30,
                )

                if isinstance(r, raw.types.upload.File):
                    while True:
                        chunk = r.bytes

                        yield chunk

                        current += 1
                        offset_bytes += chunk_size

                        if progress:
                            func = functools.partial(
                                progress,
                                min(offset_bytes, file_size)
                                if file_size != 0
                                else offset_bytes,
                                file_size,
                                *progress_args,
                            )

                            if inspect.iscoroutinefunction(progress):
                                await func()
                            else:
                                await asyncio.to_thread(func)

                        if len(chunk) < chunk_size or current >= total:
                            break

                        r = await session.invoke(
                            raw.functions.upload.GetFile(
                                location=location, offset=offset_bytes, limit=chunk_size
                            ),
                            sleep_threshold=30,
                        )
                elif isinstance(r, raw.types.upload.FileCdnRedirect):
                    auth_key = await Auth(
                        self,
                        r.dc_id,
                        await self.storage.test_mode(),
                        connection_protocol_class=self.connection_protocol_class,
                    ).create()
                    cdn_session = Session(
                        self,
                        r.dc_id,
                        auth_key,
                        await self.storage.test_mode(),
                        is_media=True,
                        is_cdn=True,
                        connection_protocol_class=self.connection_protocol_class,
                    )

                    try:
                        await cdn_session.start()

                        while True:
                            r2 = await cdn_session.invoke(
                                raw.functions.upload.GetCdnFile(
                                    file_token=r.file_token,
                                    offset=offset_bytes,
                                    limit=chunk_size,
                                )
                            )

                            if isinstance(r2, raw.types.upload.CdnFileReuploadNeeded):
                                try:
                                    await session.invoke(
                                        raw.functions.upload.ReuploadCdnFile(
                                            file_token=r.file_token,
                                            request_token=r2.request_token,
                                        )
                                    )
                                except VolumeLocNotFound:
                                    break
                                else:
                                    continue

                            chunk = r2.bytes

                            # https://core.telegram.org/cdn#decrypting-files
                            decrypted_chunk = aes.ctr256_decrypt(
                                chunk,
                                r.encryption_key,
                                bytearray(
                                    r.encryption_iv[:-4]
                                    + (offset_bytes // 16).to_bytes(4, "big")
                                ),
                            )

                            hashes = await session.invoke(
                                raw.functions.upload.GetCdnFileHashes(
                                    file_token=r.file_token, offset=offset_bytes
                                )
                            )

                            # https://core.telegram.org/cdn#verifying-files
                            for i, h in enumerate(hashes):
                                cdn_chunk = decrypted_chunk[
                                    h.limit * i : h.limit * (i + 1)
                                ]
                                CDNFileHashMismatch.check(
                                    h.hash == sha256(cdn_chunk).digest(),
                                    "h.hash == sha256(cdn_chunk).digest()",
                                )

                            yield decrypted_chunk

                            current += 1
                            offset_bytes += chunk_size

                            if progress:
                                func = functools.partial(
                                    progress,
                                    min(offset_bytes, file_size)
                                    if file_size != 0
                                    else offset_bytes,
                                    file_size,
                                    *progress_args,
                                )

                                if inspect.iscoroutinefunction(progress):
                                    await func()
                                else:
                                    await asyncio.to_thread(func)

                            if len(chunk) < chunk_size or current >= total:
                                break
                    except Exception as e:
                        raise e
                    finally:
                        await cdn_session.stop()
            except pylogram.errors.lib_errors.StopTransmission:
                raise
            except Exception as e:
                log.exception(e)
            finally:
                await session.stop()

    def guess_mime_type(self, filename: str) -> Optional[str]:
        return self.mimetypes.guess_type(filename)[0]

    def guess_extension(self, mime_type: str) -> Optional[str]:
        return self.mimetypes.guess_extension(mime_type)


class Cache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.store = {}

    def __getitem__(self, key):
        return self.store.get(key, None)

    def __setitem__(self, key, value):
        if key in self.store:
            del self.store[key]

        self.store[key] = value

        if len(self.store) > self.capacity:
            for _ in range(self.capacity // 2 + 1):
                del self.store[next(iter(self.store))]
