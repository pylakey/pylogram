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
from collections import OrderedDict
from functools import partial
from functools import update_wrapper
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional

import pylogram
import pylogram.errors.lib_errors
from pylogram import utils
from pylogram.handlers import CallbackQueryHandler
from pylogram.handlers import ChatJoinRequestHandler
from pylogram.handlers import ChatMemberUpdatedHandler
from pylogram.handlers import ChosenInlineResultHandler
from pylogram.handlers import DeletedMessagesHandler
from pylogram.handlers import EditedMessageHandler
from pylogram.handlers import InlineQueryHandler
from pylogram.handlers import MessageHandler
from pylogram.handlers import PollHandler
from pylogram.handlers import RawUpdateHandler
from pylogram.handlers import UserStatusHandler
from pylogram.handlers.handler import Handler
from pylogram.middleware import Middleware
from pylogram.raw.types import UpdateBotCallbackQuery
from pylogram.raw.types import UpdateBotChatInviteRequester
from pylogram.raw.types import UpdateBotInlineQuery
from pylogram.raw.types import UpdateBotInlineSend
from pylogram.raw.types import UpdateChannelParticipant
from pylogram.raw.types import UpdateChatParticipant
from pylogram.raw.types import UpdateDeleteChannelMessages
from pylogram.raw.types import UpdateDeleteMessages
from pylogram.raw.types import UpdateEditChannelMessage
from pylogram.raw.types import UpdateEditMessage
from pylogram.raw.types import UpdateInlineBotCallbackQuery
from pylogram.raw.types import UpdateMessagePoll
from pylogram.raw.types import UpdateNewChannelMessage
from pylogram.raw.types import UpdateNewMessage
from pylogram.raw.types import UpdateNewScheduledMessage
from pylogram.raw.types import UpdateUserStatus

log = logging.getLogger(__name__)


class Dispatcher:
    NEW_MESSAGE_UPDATES = (UpdateNewMessage, UpdateNewChannelMessage, UpdateNewScheduledMessage)
    EDIT_MESSAGE_UPDATES = (UpdateEditMessage, UpdateEditChannelMessage)
    DELETE_MESSAGES_UPDATES = (UpdateDeleteMessages, UpdateDeleteChannelMessages)
    CALLBACK_QUERY_UPDATES = (UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery)
    CHAT_MEMBER_UPDATES = (UpdateChatParticipant, UpdateChannelParticipant)
    USER_STATUS_UPDATES = (UpdateUserStatus,)
    BOT_INLINE_QUERY_UPDATES = (UpdateBotInlineQuery,)
    POLL_UPDATES = (UpdateMessagePoll,)
    CHOSEN_INLINE_RESULT_UPDATES = (UpdateBotInlineSend,)
    CHAT_JOIN_REQUEST_UPDATES = (UpdateBotChatInviteRequester,)

    def __init__(self, client: "pylogram.Client"):
        self.client = client
        self.handler_worker_tasks = []
        self.locks_list = []
        self.updates_queue = asyncio.Queue()
        self.groups: dict[int, set[Handler]] = OrderedDict()
        self.middlewares: List[Middleware] = []
        self.__middlewares_handlers: Iterable[Middleware]
        self.__run_middlewares: Optional[bool] = None

        async def message_parser(update, users, chats):
            return (
                await pylogram.types.Message._parse(
                    self.client,
                    update.message,
                    users,
                    chats,
                    isinstance(update, UpdateNewScheduledMessage)
                ),
                MessageHandler
            )

        async def edited_message_parser(update, users, chats):
            # Edited messages are parsed the same way as new messages, but the handler is different
            parsed, _ = await message_parser(update, users, chats)
            return parsed, EditedMessageHandler

        async def deleted_messages_parser(update, users, chats):
            return (
                utils.parse_deleted_messages(self.client, update),
                DeletedMessagesHandler
            )

        async def callback_query_parser(update, users, chats):
            return (
                await pylogram.types.CallbackQuery._parse(self.client, update, users),
                CallbackQueryHandler
            )

        async def user_status_parser(update, users, chats):
            return (
                pylogram.types.User._parse_user_status(self.client, update),
                UserStatusHandler
            )

        async def inline_query_parser(update, users, chats):
            return (
                pylogram.types.InlineQuery._parse(self.client, update, users),
                InlineQueryHandler
            )

        async def poll_parser(update, users, chats):
            return (
                pylogram.types.Poll._parse_update(self.client, update),
                PollHandler
            )

        async def chosen_inline_result_parser(update, users, chats):
            return (
                pylogram.types.ChosenInlineResult._parse(self.client, update, users),
                ChosenInlineResultHandler
            )

        async def chat_member_updated_parser(update, users, chats):
            return (
                pylogram.types.ChatMemberUpdated._parse(self.client, update, users, chats),
                ChatMemberUpdatedHandler
            )

        async def chat_join_request_parser(update, users, chats):
            return (
                pylogram.types.ChatJoinRequest._parse(self.client, update, users, chats),
                ChatJoinRequestHandler
            )

        self.update_parsers = {
            Dispatcher.NEW_MESSAGE_UPDATES: message_parser,
            Dispatcher.EDIT_MESSAGE_UPDATES: edited_message_parser,
            Dispatcher.DELETE_MESSAGES_UPDATES: deleted_messages_parser,
            Dispatcher.CALLBACK_QUERY_UPDATES: callback_query_parser,
            Dispatcher.USER_STATUS_UPDATES: user_status_parser,
            Dispatcher.BOT_INLINE_QUERY_UPDATES: inline_query_parser,
            Dispatcher.POLL_UPDATES: poll_parser,
            Dispatcher.CHOSEN_INLINE_RESULT_UPDATES: chosen_inline_result_parser,
            Dispatcher.CHAT_MEMBER_UPDATES: chat_member_updated_parser,
            Dispatcher.CHAT_JOIN_REQUEST_UPDATES: chat_join_request_parser
        }
        self.update_parsers = {key: value for key_tuple, value in self.update_parsers.items() for key in key_tuple}

    async def start(self):
        self.__middlewares_handlers = tuple(self.__prepare_middlewares())
        self.__run_middlewares = True if self.middlewares else False

        if not self.client.no_updates:
            for i in range(self.client.workers):
                self.locks_list.append(lock := asyncio.Lock())
                self.handler_worker_tasks.append(asyncio.create_task(self.handler_worker(lock)))

            log.info("Started %s HandlerTasks", self.client.workers)

    async def stop(self):
        if not self.client.no_updates:
            for i in range(self.client.workers):
                self.updates_queue.put_nowait(None)

            for i in self.handler_worker_tasks:
                await i

            self.handler_worker_tasks.clear()
            self.groups.clear()

            log.info("Stopped %s HandlerTasks", self.client.workers)

    def add_handler(self, handler, group: int):
        self.groups.setdefault(group, set()).add(handler)
        self.groups = OrderedDict(sorted(self.groups.items()))
        log.debug(f"Added handler %s to group %s. Groups: {self.groups}", handler, group)

    def remove_handler(self, handler, group: int):
        self.groups.setdefault(group, set()).discard(handler)
        log.debug("Removed handler %s from group %s", handler, group)

    def add_middleware(self, middleware: Middleware):
        self.middlewares.append(middleware)

    def remove_middleware(self, middleware: Middleware):
        self.middlewares.remove(middleware)

    def __prepare_middlewares(self) -> Iterator[Middleware]:
        yield from reversed(self.middlewares)

    async def handle_update_with_middlewares(self, update, parsed_update, handler_type, users, chats):
        async def fn(*_, **__):
            return await self.handle_update(update, parsed_update, handler_type, users, chats)

        call_next = fn

        for m in self.__middlewares_handlers:
            call_next = update_wrapper(partial(m, call_next=call_next), call_next)

        return await call_next(self.client, parsed_update)

    async def handler_worker(self, lock):
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                update, users, chats = packet
                parser = self.update_parsers.get(type(update), None)

                parsed_update, handler_type = (
                    await parser(update, users, chats)
                    if parser is not None
                    else (None, type(None))
                )

                async with lock:
                    if bool(parsed_update) and self.__run_middlewares:
                        await self.handle_update_with_middlewares(update, parsed_update, handler_type, users, chats)
                    else:
                        await self.handle_update(update, parsed_update, handler_type, users, chats)
            except pylogram.errors.lib_errors.StopPropagation:
                continue
            except Exception as e:
                log.exception(e)

    async def handle_update(self, update, parsed_update, handler_type, users, chats):
        for group_id, group in self.groups.items():
            for handler in group.copy():
                args = None

                if isinstance(handler, handler_type):
                    try:
                        if await handler.check(self.client, parsed_update):
                            args = (parsed_update,)
                    except Exception as e:
                        log.exception(e)
                        continue
                elif isinstance(handler, RawUpdateHandler):
                    args = (update, users, chats)

                if args is None:
                    continue

                try:
                    await handler.callback(self.client, *args)
                except pylogram.errors.lib_errors.StopPropagation:
                    raise
                except pylogram.errors.lib_errors.ContinuePropagation:
                    continue
                except Exception as e:
                    log.exception(e)

                break
