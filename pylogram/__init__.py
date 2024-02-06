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

__version__ = "0.1.6"
__license__ = "GNU Lesser General Public License v3.0 (LGPL-3.0)"
__copyright__ = "Copyright (C) 2017-present Dan <https://github.com/delivrance>"

from concurrent.futures.thread import ThreadPoolExecutor

from . import crypto
from . import emoji
from . import enums
from . import errors
from . import file_id
from . import filters
from . import handlers
from . import methods
from . import middleware
from . import mime_types
from . import raw
from . import session
from . import storage
from . import types
from . import utils
from .client import Client
from .dispatcher import Dispatcher

crypto_executor = ThreadPoolExecutor(1, thread_name_prefix="CryptoWorker")
