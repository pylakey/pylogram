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

from datetime import datetime
from typing import List
from typing import Optional
from typing import Union

import pylogram
from pylogram import enums
from pylogram import raw
from pylogram import types
from pylogram import utils


class SendMessage:
    async def send_message(
            self: "pylogram.Client",
            chat_id: Union[int, str],
            text: str,
            parse_mode: Optional["enums.ParseMode"] = None,
            entities: List["types.MessageEntity"] = None,
            disable_web_page_preview: bool = None,
            disable_notification: bool = None,
            reply_to: Union[int, raw.types.InputReplyToMessage, raw.types.InputReplyToStory] = None,
            schedule_date: datetime = None,
            protect_content: bool = None,
            reply_markup: Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply"
            ] = None
    ) -> "types.Message":
        """Send text messages.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            parse_mode (:obj:`~pylogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pylogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to (``int``, *optional*):
                If the message is a reply, ID of the original message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            reply_markup (:obj:`~pylogram.types.InlineKeyboardMarkup` | :obj:`~pylogram.types.ReplyKeyboardMarkup` | :obj:`~pylogram.types.ReplyKeyboardRemove` | :obj:`~pylogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pylogram.types.Message`: On success, the sent text message is returned.

        Example:
            .. code-block:: python

                # Simple example
                await app.send_message("me", "Message sent with **Pylogram**!")

                # Disable web page previews
                await app.send_message("me", "https://example.com",
                    disable_web_page_preview=True)

                # Reply to a message using its id
                await app.send_message("me", "this is a reply", reply_to=123)

            .. code-block:: python

                # For bots only, send messages with keyboards attached

                from pylogram.types import (
                    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)

                # Send a normal keyboard
                await app.send_message(
                    chat_id, "Look at that button!",
                    reply_markup=ReplyKeyboardMarkup([["Nice!"]]))

                # Send an inline keyboard
                await app.send_message(
                    chat_id, "These are inline buttons",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Data", callback_data="callback_data")],
                            [InlineKeyboardButton("Example Url", url="https://example.com")]
                        ]))
        """

        message, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()

        r = await self.invoke(
            raw.functions.messages.SendMessage(
                peer=await self.resolve_peer(chat_id),
                no_webpage=disable_web_page_preview or None,
                silent=disable_notification or None,
                reply_to=raw.types.InputReplyToMessage(
                    reply_to_msg_id=reply_to
                ) if isinstance(reply_to, int) else reply_to,
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=entities,
                noforwards=protect_content
            )
        )

        if isinstance(r, raw.types.UpdateShortSentMessage):
            peer = await self.resolve_peer(chat_id)

            peer_id = (
                peer.user_id
                if isinstance(peer, raw.types.InputPeerUser)
                else -peer.chat_id
            )

            return types.Message(
                id=r.id,
                chat=types.Chat(
                    id=peer_id,
                    type=enums.ChatType.PRIVATE,
                    client=self
                ),
                text=message,
                date=utils.timestamp_to_datetime(r.date),
                outgoing=r.out,
                reply_markup=reply_markup,
                entities=[
                    types.MessageEntity._parse(None, entity, {})
                    for entity in entities
                ] if entities else None,
                client=self
            )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                              raw.types.UpdateNewChannelMessage,
                              raw.types.UpdateNewScheduledMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage)
                )
