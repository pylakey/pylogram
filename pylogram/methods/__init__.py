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

from .account import Account
from .advanced import Advanced
from .auth import Auth
from .bots import Bots
from .business import Business
from .chat_lists import ChatLists
from .chats import Chats
from .contacts import Contacts
from .decorators import Decorators
from .forums import Forums
from .help import Help
from .invite_links import InviteLinks
from .messages import Messages
from .password import Password
from .premium import Premium
from .users import Users
from .utilities import Utilities


class Methods(
    Account,
    Advanced,
    Auth,
    Bots,
    Business,
    ChatLists,
    Chats,
    Contacts,
    Decorators,
    Forums,
    Help,
    InviteLinks,
    Messages,
    Password,
    Premium,
    Users,
    Utilities,
):
    pass
