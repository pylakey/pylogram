"""Per-channel asyncio task managing its own SequenceBox and gap recovery."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TYPE_CHECKING

from .sequence_box import SequenceBox
from .types import PendingUpdate

if TYPE_CHECKING:
    from .types import UpdatesConfig

log = logging.getLogger(__name__)


class ChannelState:
    """Asyncio task that processes updates for one channel.

    Lifecycle:
    - Created lazily when the first update for a channel arrives.
    - Runs an async loop consuming updates from an internal queue.
    - If no updates arrive within ``config.channel_idle_timeout`` seconds, the
      task finishes and persists its pts so the next update can re-create it.
    - Gap recovery: if a gap is detected, waits ``config.gap_timeout`` seconds
      before calling getChannelDifference.
    """

    def __init__(
        self,
        channel_id: int,
        access_hash: int,
        initial_pts: int,
        config: "UpdatesConfig",
        deliver: Callable[..., Any],
        get_difference: Callable[[int], Awaitable[None]],
    ) -> None:
        self.channel_id = channel_id
        self.access_hash = access_hash
        self._box = SequenceBox()
        self._box.state = initial_pts
        self._queue: asyncio.Queue[PendingUpdate | object] = asyncio.Queue()
        self._config = config
        self._deliver = deliver
        self._get_difference = get_difference
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name=f"channel-{self.channel_id}")

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._config.set_channel_pts(self.channel_id, self._box.state)

    def feed(self, update: PendingUpdate) -> None:
        """Queue an update for processing. Called from UpdatesManager."""
        self._queue.put_nowait(update)

    @property
    def pts(self) -> int:
        return self._box.state

    def apply_difference(self, new_pts: int) -> list:
        """Apply channel difference result. Returns drained pending updates."""
        return self._box.apply_difference(new_pts)

    def set_pts(self, new_pts: int) -> None:
        """Set channel pts directly (for DifferenceEmpty/TooLong)."""
        self._box.state = new_pts

    async def _run(self) -> None:
        # Sentinel objects -- identifiable by identity, not type
        _GAP_SENTINEL = object()

        gap_task: asyncio.Task | None = None

        while True:
            try:
                item = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self._config.channel_idle_timeout,
                )
            except (asyncio.TimeoutError, TimeoutError):
                log.debug("ChannelState %d idle -- cleaning up", self.channel_id)
                break

            # Gap timeout sentinel
            if item is _GAP_SENTINEL:
                gap_task = None
                await self._get_difference(self.channel_id)
                continue

            assert isinstance(item, PendingUpdate)
            result = self._box.feed(item)

            if result is not None:
                # Gap filled (or no gap) -- cancel pending timer
                if gap_task is not None:
                    gap_task.cancel()
                    gap_task = None
                for u in result:
                    self._deliver(u.update, u.users, u.chats)

            elif self._box.has_gap and gap_task is None:
                # Gap detected -- start timer
                async def _send_gap_sentinel(sentinel=_GAP_SENTINEL) -> None:
                    await asyncio.sleep(self._config.gap_timeout)
                    self._queue.put_nowait(sentinel)

                gap_task = asyncio.create_task(_send_gap_sentinel())

        # Persist pts on idle exit
        await self._config.set_channel_pts(self.channel_id, self._box.state)
