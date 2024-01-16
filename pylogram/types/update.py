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
import json
from typing import Any
from typing import Dict

import pylogram
import pylogram.errors.lib_errors


class UpdateBucket(object):
    _bucket: Dict[str, Any] = {}

    def __setattr__(self, key: str, value: Any):
        if key in ['_bucket', 'clear', 'set', 'update', 'json', 'parse_json']:
            raise ValueError(f'You are unable to change {key} attribute')

        self._bucket[key.lower()] = value
        return value

    def __getattribute__(self, name):
        if name in ['_bucket', 'clear', 'set', 'update', 'json', 'parse_json']:
            return object.__getattribute__(self, name)

        bucket = object.__getattribute__(self, '_bucket')
        item = bucket.get(name)

        if not bool(item):
            return object.__getattribute__(self, name)

        return item

    def clear(self):
        self._bucket.clear()

    def set(self, data: Dict[str, Any] = None, **kwargs):
        self.clear()
        self.update(data, **kwargs)

    def update(self, data: Dict[str, Any] = None, **kwargs):
        if data is None:
            data = {}

        self._bucket.update(data)
        self._bucket.update(kwargs)
        return self._bucket

    def json(self, **kwargs) -> str:
        return json.dumps(self._bucket, **kwargs)

    def parse_json(self, json_string: str):
        self.set(json.loads(json_string))


class Update:
    bucket: UpdateBucket = UpdateBucket()

    def stop_propagation(self):
        raise pylogram.errors.lib_errors.StopPropagation

    def continue_propagation(self):
        raise pylogram.errors.lib_errors.ContinuePropagation
