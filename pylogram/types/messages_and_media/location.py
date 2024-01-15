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

from pylogram import raw
from ..object import Object


class Location(Object):
    """A point on the map.

    Parameters:
        longitude (``float``):
            Longitude as defined by sender.

        latitude (``float``):
            Latitude as defined by sender.
    """

    def __init__(
        self,
        *,
        client: "pylogram.Client" = None,
        longitude: float,
        latitude: float
    ):
        super().__init__(client)

        self.longitude = longitude
        self.latitude = latitude

    @staticmethod
    def _parse(client, geo_point: "raw.types.GeoPoint") -> "Location":
        if isinstance(geo_point, raw.types.GeoPoint):
            return Location(
                longitude=geo_point.long,
                latitude=geo_point.lat,
                client=client
            )
