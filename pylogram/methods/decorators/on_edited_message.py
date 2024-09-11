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
from pylogram.filters import Filter
from pylogram.typevars import HandlerCallable
from pylogram.typevars import HandlerDecorator


class OnEditedMessage:
    def on_edited_message(
        self=None,
        filters=None,
        group: int = 0
    ) -> HandlerDecorator:
        """Decorator for handling edited messages.

        This does the same thing as :meth:`~pylogram.Client.add_handler` using the
        :obj:`~pylogram.handlers.EditedMessageHandler`.

        Parameters:
            filters (:obj:`~pylogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: HandlerCallable) -> HandlerCallable:
            if isinstance(self, pylogram.Client):
                self.add_handler(pylogram.handlers.EditedMessageHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        pylogram.handlers.EditedMessageHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
