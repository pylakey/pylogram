from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PendingUpdate:
    """Wraps any sequenced update with its metadata."""

    update: Any  # raw TLObject
    pts: int  # sequence state AFTER this update
    pts_count: int  # how many sequence numbers consumed
    users: dict[int, Any]
    chats: dict[int, Any]

    @property
    def start(self) -> int:
        """Sequence state BEFORE this update: pts - pts_count."""
        return self.pts - self.pts_count

    @property
    def end(self) -> int:
        """Sequence state AFTER this update: pts."""
        return self.pts


@dataclass
class UpdatesConfig:
    """All dependencies and tuning knobs for UpdatesManager.

    Required callbacks are wired automatically by Client when
    ``updates_config`` is not passed explicitly.
    """

    # --- Delivery callbacks (required) ---
    on_update: Callable[[Any, dict, dict], Any]
    """Deliver one ordered update. Signature: (update, users, chats) -> None."""

    on_peers: Callable[[list, list], Awaitable[Any]]
    """Cache users/chats from a container. Called BEFORE dispatching inner updates."""

    invoke: Callable[[Any, float], Awaitable[Any]]
    """Send a TL query. Signature: (query, timeout) -> result."""

    get_channel_access_hash: Callable[[int], Awaitable[int | None]]
    """Return cached access_hash for a channel, or None."""

    get_peer: Callable[[int], Awaitable[Any | None]]
    """Return a cached peer object by id, or None."""

    get_my_user_id: Callable[[], Awaitable[int]]
    """Return the current user's id (for synthesising outgoing short messages)."""

    # --- State persistence callbacks (required) ---
    get_state: Callable[[], Awaitable[tuple[int, int, int, int] | None]]
    """Load (pts, qts, seq, date). Returns None if not yet persisted."""

    set_state: Callable[[int, int, int, int], Awaitable[None]]
    """Persist (pts, qts, seq, date)."""

    get_channel_pts: Callable[[int], Awaitable[int | None]]
    """Load pts for a channel, or None."""

    set_channel_pts: Callable[[int, int], Awaitable[None]]
    """Persist pts for a channel."""

    # --- Feature toggle ---
    enabled: bool = True
    """False = bypass gap recovery (passthrough to dispatcher)."""

    # --- Tuning ---
    gap_timeout: float = 1.5
    """Seconds to wait for out-of-order updates before calling getDifference."""

    idle_timeout: float = 900.0
    """Seconds with no updates before calling getDifference as a safety net."""

    channel_idle_timeout: float = 900.0
    """Seconds of inactivity before a channel task is cleaned up."""

    diff_limit: int = 100
    """pts_total_limit for getChannelDifference (user accounts)."""

    diff_limit_bot: int = 100_000
    """pts_total_limit for getChannelDifference (bot accounts)."""

    first_sync_limit: int = 5_000
    """pts_total_limit for the first getDifference after startup."""

    is_bot: bool = False
    """Controls which diff_limit is used."""
