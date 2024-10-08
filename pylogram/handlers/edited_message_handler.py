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

from typing import Callable

from .handler import Handler
from .handler import HandlerCallable


class EditedMessageHandler(Handler):
    """The EditedMessage handler class. Used to handle edited messages.
     It is intended to be used with :meth:`~pylogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pylogram.Client.on_edited_message` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new edited message arrives. It takes *(client, message)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pylogram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        edited_message (:obj:`~pylogram.types.Message`):
            The received edited message.
    """

    def __init__(self, callback: HandlerCallable, filters=None):
        super().__init__(callback, filters)
