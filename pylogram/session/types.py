from __future__ import annotations

from dataclasses import dataclass, fields

from pylogram import raw


@dataclass(slots=True)
class ConnectionParams:
    """Parameters for ``initConnection``'s ``params`` (JSONValue) field.

    All fields are optional.  Only non-``None`` fields are serialised
    into the TL ``JsonObject`` sent to Telegram.

    Reference: the official Android client sends these keys inside
    ``initConnection#c1cd5ea9``.
    """

    device_token: str | None = None
    """Push notification token (Firebase / Huawei)."""

    data: str | None = None
    """Certificate fingerprint (SHA-256 hex of the signing cert)."""

    installer: str | None = None
    """Package name of the app that installed this client."""

    package_id: str | None = None
    """Package name of this application."""

    tz_offset: int | None = None
    """Timezone offset from UTC in seconds (e.g. 10800 for UTC+3)."""

    perf_cat: int | None = None
    """Device performance category (1 = low, 2 = average, 3 = high)."""

    def to_json_object(self) -> raw.types.JsonObject:
        """Convert non-``None`` fields to a TL ``JsonObject``.

        String fields become ``JsonString``, numeric fields become
        ``JsonNumber``.  Fields set to ``None`` are omitted.
        """
        entries: list[raw.types.JsonObjectValue] = []

        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue

            if isinstance(value, str):
                json_val = raw.types.JsonString(value=value)
            elif isinstance(value, (int, float)):
                json_val = raw.types.JsonNumber(value=float(value))
            else:
                continue

            entries.append(
                raw.types.JsonObjectValue(key=f.name, value=json_val)
            )

        return raw.types.JsonObject(value=entries)
