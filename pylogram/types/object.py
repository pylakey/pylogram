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

import typing
from datetime import datetime
from enum import Enum
from json import dumps

import pylogram

RawType = typing.TypeVar("RawType", bound=pylogram.raw.core.TLObject, covariant=True)


class Object(typing.Generic[RawType]):
    def __init__(
        self,
        client: "pylogram.Client" = None,
        *,
        _raw: RawType = None,
    ):
        self._client = client
        self._raw = _raw

    def bind(self, client: "pylogram.Client"):
        """Bind a Client instance to this and to all nested Pylogram objects.

        Parameters:
            client (:obj:`~pylogram.types.Client`):
                The Client instance to bind this object with. Useful to re-enable bound methods after serializing and
                deserializing Pylogram objects with ``repr`` and ``eval``.
        """
        self._client = client

        for i in self.__dict__:
            o = getattr(self, i)

            if isinstance(o, Object):
                o.bind(client)

    @staticmethod
    def default(obj: "Object"):
        if isinstance(obj, bytes):
            return repr(obj)

        # https://t.me/pylogramchat/167281
        # Instead of re.Match, which breaks for python <=3.6
        if isinstance(obj, typing.Match):
            return repr(obj)

        if isinstance(obj, Enum):
            return str(obj.value)

        if isinstance(obj, datetime):
            return str(obj)

        return {
            "_": obj.__class__.__name__,
            **{
                attr: getattr(obj, attr)
                for attr in filter(
                    lambda x: not x.startswith("_"),
                    getattr(obj, "__dict__", getattr(obj, "__slots__", {})) or {},
                )
                if getattr(obj, attr) is not None
            },
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=Object.default, ensure_ascii=False)

    def __repr__(self) -> str:
        return "pylogram.types.{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{attr}={repr(getattr(self, attr))}"
                for attr in filter(lambda x: not x.startswith("_"), self.__dict__)
                if getattr(self, attr) is not None
            ),
        )

    def __eq__(self, other: "Object") -> bool:
        for attr in self.__dict__:
            try:
                if attr.startswith("_"):
                    continue

                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True

    def __setstate__(self, state):
        for attr in state:
            obj = state[attr]

            # Maybe a better alternative would be https://docs.python.org/3/library/inspect.html#inspect.signature
            if isinstance(obj, tuple) and len(obj) == 2 and obj[0] == "dt":
                state[attr] = datetime.fromtimestamp(obj[1])

        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_client", None)

        for attr in state:
            obj = state[attr]

            if isinstance(obj, datetime):
                state[attr] = ("dt", obj.timestamp())

        return state

    def get_raw(self) -> typing.Optional[RawType]:
        return self._raw
