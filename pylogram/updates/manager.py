"""UpdatesManager — main orchestrator for gap recovery.

Processing pipeline:
  Session → Client.handle_updates → UpdatesManager.handle
    ├─ Updates / UpdatesCombined → on_peers → seq box → per-update dispatch
    ├─ UpdateShortMessage / UpdateShortChatMessage → peer check → synthesise → pts box
    ├─ UpdateShort → classify inner update → dispatch
    └─ UpdatesTooLong → getDifference immediately
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from pylogram import raw

from .channel_state import ChannelState
from .sequence_box import SequenceBox
from .short import convert_short_update
from .types import PendingUpdate
from .utils import (
    UPDATE_TYPE_CHANNEL,
    UPDATE_TYPE_NONE,
    UPDATE_TYPE_PTS,
    UPDATE_TYPE_QTS,
    get_update_channel_id,
    get_update_pts,
    get_update_pts_count,
    get_update_qts,
    get_update_type,
)

if TYPE_CHECKING:
    from .types import UpdatesConfig

log = logging.getLogger(__name__)

# Sentinel for gap/idle timeouts injected into the main queue
_PTS_GAP = object()
_QTS_GAP = object()
_SEQ_GAP = object()
_IDLE = object()


class UpdatesManager:
    """Receives raw Telegram update containers, enforces ordering, and delivers
    individual updates to ``config.on_update`` in pts/qts/seq order.
    """

    def __init__(self, config: UpdatesConfig) -> None:
        self._config = config
        self._pts_box = SequenceBox()
        self._qts_box = SequenceBox()
        self._seq_box = SequenceBox()
        self._date = 0
        self._channels: dict[int, ChannelState] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._task: asyncio.Task | None = None
        self._is_bot: bool = config.is_bot

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Load persisted state (or call getState), then start the event loop."""
        persisted = await self._config.get_state()
        if persisted is None:
            log.debug("No persisted update state — calling getState")
            result = await self._config.invoke(
                raw.functions.updates.GetState(),
                15.0,
            )
            self._pts_box.state = result.pts
            self._qts_box.state = result.qts
            self._seq_box.state = result.seq
            self._date = result.date
            await self._config.set_state(result.pts, result.qts, result.seq, result.date)
        else:
            pts, qts, seq, date = persisted
            log.debug("Loaded update state: pts=%d qts=%d seq=%d date=%d", pts, qts, seq, date)
            self._pts_box.state = pts
            self._qts_box.state = qts
            self._seq_box.state = seq
            self._date = date
            if pts > 0:
                log.debug("Recovering missed updates via getDifference")
                await self._get_difference(first_sync=True)

        self._task = asyncio.create_task(self._run(), name="updates-manager")

    async def stop(self) -> None:
        """Persist state, stop all channel tasks, stop the event loop."""
        for ch in list(self._channels.values()):
            await ch.stop()
        self._channels.clear()

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self._save_state()

    async def handle(self, updates: object) -> None:
        """Entry point from Client.handle_updates(). Non-blocking."""
        await self._queue.put(updates)

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        pts_gap_task: asyncio.Task | None = None
        qts_gap_task: asyncio.Task | None = None
        seq_gap_task: asyncio.Task | None = None

        async def _after(delay: float, sentinel: object) -> None:
            await asyncio.sleep(delay)
            self._queue.put_nowait(sentinel)

        idle_task: asyncio.Task = asyncio.create_task(
            _after(self._config.idle_timeout, _IDLE)
        )

        try:
            while True:
                item = await self._queue.get()

                if item is _IDLE:
                    idle_task = asyncio.create_task(_after(self._config.idle_timeout, _IDLE))
                    await self._get_difference()
                    continue

                if item is _PTS_GAP:
                    pts_gap_task = None
                    await self._get_difference()
                    continue

                if item is _QTS_GAP:
                    qts_gap_task = None
                    await self._get_difference()
                    continue

                if item is _SEQ_GAP:
                    seq_gap_task = None
                    await self._get_difference()
                    continue

                # Real Telegram update — reset idle timer
                idle_task.cancel()
                idle_task = asyncio.create_task(_after(self._config.idle_timeout, _IDLE))

                try:
                    await self._dispatch_container(item)
                except Exception:
                    log.exception("Unhandled error processing update %s — continuing", type(item).__name__)
                    continue

                # Sync gap timers with box states
                if self._pts_box.has_gap and pts_gap_task is None:
                    pts_gap_task = asyncio.create_task(_after(self._config.gap_timeout, _PTS_GAP))
                elif not self._pts_box.has_gap and pts_gap_task:
                    pts_gap_task.cancel()
                    pts_gap_task = None

                if self._qts_box.has_gap and qts_gap_task is None:
                    qts_gap_task = asyncio.create_task(_after(self._config.gap_timeout, _QTS_GAP))
                elif not self._qts_box.has_gap and qts_gap_task:
                    qts_gap_task.cancel()
                    qts_gap_task = None

                if self._seq_box.has_gap and seq_gap_task is None:
                    seq_gap_task = asyncio.create_task(_after(self._config.gap_timeout, _SEQ_GAP))
                elif not self._seq_box.has_gap and seq_gap_task:
                    seq_gap_task.cancel()
                    seq_gap_task = None

        finally:
            idle_task.cancel()
            for t in [pts_gap_task, qts_gap_task, seq_gap_task]:
                if t:
                    t.cancel()

    # ------------------------------------------------------------------
    # Container dispatch
    # ------------------------------------------------------------------

    async def _dispatch_container(self, updates: object) -> None:
        if isinstance(updates, (raw.types.Updates, raw.types.UpdatesCombined)):
            await self._handle_combined(updates)
        elif isinstance(updates, (raw.types.UpdateShortMessage, raw.types.UpdateShortChatMessage)):
            await self._handle_short_message(updates)
        elif isinstance(updates, raw.types.UpdateShort):
            await self._handle_update_short(updates)
        elif isinstance(updates, raw.types.UpdatesTooLong):
            log.info("UpdatesTooLong received — calling getDifference")
            await self._get_difference()
        else:
            log.debug("Unhandled container type: %s", type(updates).__name__)

    async def _handle_combined(
        self,
        updates: raw.types.Updates | raw.types.UpdatesCombined,
    ) -> None:
        # 1. Cache peers BEFORE dispatching
        await self._config.on_peers(updates.users, updates.chats)
        users = {u.id: u for u in updates.users}
        chats = {c.id: c for c in updates.chats}

        # 2. Seq validation (seq=0 means skip)
        seq = getattr(updates, "seq", 0)
        if seq != 0:
            seq_start = getattr(updates, "seq_start", seq)
            pts_count = seq - seq_start + 1
            seq_pending = PendingUpdate(
                update=updates,
                pts=seq,
                pts_count=pts_count,
                users=users,
                chats=chats,
            )
            ready = self._seq_box.feed(seq_pending)
            if ready is None:
                return  # buffered or ignored
            for r in ready:
                await self._dispatch_inner(r.update, r.users, r.chats)
        else:
            await self._dispatch_inner(updates, users, chats)

    async def _dispatch_inner(
        self,
        container: raw.types.Updates | raw.types.UpdatesCombined,
        users: dict,
        chats: dict,
    ) -> None:
        for update in container.updates:
            utype = get_update_type(update)

            if utype == UPDATE_TYPE_PTS:
                pending = PendingUpdate(
                    update=update,
                    pts=get_update_pts(update),
                    pts_count=get_update_pts_count(update),
                    users=users,
                    chats=chats,
                )
                result = self._pts_box.feed(pending)
                if result is not None:
                    for r in result:
                        self._deliver(r)

            elif utype == UPDATE_TYPE_QTS:
                pending = PendingUpdate(
                    update=update,
                    pts=get_update_qts(update),
                    pts_count=1,
                    users=users,
                    chats=chats,
                )
                result = self._qts_box.feed(pending)
                if result is not None:
                    for r in result:
                        self._deliver(r)

            elif utype == UPDATE_TYPE_CHANNEL:
                channel_id = get_update_channel_id(update)
                if channel_id is None:
                    log.warning("Channel update with no channel_id: %s", type(update).__name__)
                    continue
                await self._feed_channel(
                    channel_id,
                    PendingUpdate(
                        update=update,
                        pts=get_update_pts(update),
                        pts_count=get_update_pts_count(update),
                        users=users,
                        chats=chats,
                    ),
                )

            else:  # TYPE_NONE
                self._config.on_update(update, users, chats)

        self._date = getattr(container, "date", self._date) or self._date
        await self._save_state()

    async def _handle_short_message(
        self,
        update: raw.types.UpdateShortMessage | raw.types.UpdateShortChatMessage,
    ) -> None:
        my_user_id = await self._config.get_my_user_id()
        converted = await convert_short_update(update, self._config.get_peer, my_user_id)

        if converted is None:
            # Missing peer — fall back to getDifference (Android behaviour)
            log.debug("Short update: missing peer, falling back to getDifference")
            await self._get_difference()
            return

        pending = PendingUpdate(
            update=converted,
            pts=converted.pts,
            pts_count=converted.pts_count,
            users={},
            chats={},
        )
        result = self._pts_box.feed(pending)
        if result is not None:
            for r in result:
                self._deliver(r)

        self._date = update.date
        await self._save_state()

    async def _handle_update_short(self, update: raw.types.UpdateShort) -> None:
        inner = update.update
        utype = get_update_type(inner)

        if utype == UPDATE_TYPE_PTS:
            pending = PendingUpdate(
                update=inner,
                pts=get_update_pts(inner),
                pts_count=get_update_pts_count(inner),
                users={},
                chats={},
            )
            result = self._pts_box.feed(pending)
            if result is not None:
                for r in result:
                    self._deliver(r)

        elif utype == UPDATE_TYPE_QTS:
            pending = PendingUpdate(
                update=inner,
                pts=get_update_qts(inner),
                pts_count=1,
                users={},
                chats={},
            )
            result = self._qts_box.feed(pending)
            if result is not None:
                for r in result:
                    self._deliver(r)

        elif utype == UPDATE_TYPE_CHANNEL:
            channel_id = get_update_channel_id(inner)
            if channel_id:
                await self._feed_channel(
                    channel_id,
                    PendingUpdate(
                        update=inner,
                        pts=get_update_pts(inner),
                        pts_count=get_update_pts_count(inner),
                        users={},
                        chats={},
                    ),
                )
        else:
            self._config.on_update(inner, {}, {})

        self._date = update.date
        await self._save_state()

    # ------------------------------------------------------------------
    # Channel state management
    # ------------------------------------------------------------------

    async def _feed_channel(self, channel_id: int, pending: PendingUpdate) -> None:
        if channel_id not in self._channels:
            await self._create_channel_state(channel_id, pending)
        if channel_id in self._channels:
            self._channels[channel_id].feed(pending)

    async def _create_channel_state(self, channel_id: int, first_update: PendingUpdate) -> None:
        access_hash = await self._config.get_channel_access_hash(channel_id)
        if access_hash is None:
            log.warning("No access_hash for channel %d — dropping update", channel_id)
            return

        stored_pts = await self._config.get_channel_pts(channel_id)
        initial_pts = stored_pts if stored_pts is not None else first_update.start

        async def _get_channel_diff(cid: int) -> None:
            await self._get_channel_difference(cid)

        state = ChannelState(
            channel_id=channel_id,
            access_hash=access_hash,
            initial_pts=initial_pts,
            config=self._config,
            deliver=self._config.on_update,
            get_difference=_get_channel_diff,
        )
        self._channels[channel_id] = state
        state.start()

        def _on_channel_done(t: asyncio.Task, cid: int = channel_id) -> None:
            self._channels.pop(cid, None)

        state._task.add_done_callback(_on_channel_done)

    # ------------------------------------------------------------------
    # getDifference
    # ------------------------------------------------------------------

    async def _get_difference(self, first_sync: bool = False) -> None:
        self._pts_box.clear_gaps()
        self._qts_box.clear_gaps()
        self._seq_box.clear_gaps()

        limit = self._config.first_sync_limit if first_sync else None

        try:
            diff = await self._config.invoke(
                raw.functions.updates.GetDifference(
                    pts=self._pts_box.state,
                    date=self._date,
                    qts=self._qts_box.state or -1,
                    pts_total_limit=limit,
                ),
                60.0,
            )
        except Exception as e:
            log.warning("getDifference failed: %s", e)
            return

        await self._apply_difference(diff)

    async def _apply_difference(self, diff: object) -> None:
        if isinstance(diff, raw.types.updates.DifferenceEmpty):
            self._date = diff.date
            self._seq_box.state = diff.seq
            await self._save_state()

        elif isinstance(diff, raw.types.updates.Difference):
            await self._apply_full_difference(diff)

        elif isinstance(diff, raw.types.updates.DifferenceSlice):
            await self._apply_full_difference(diff)
            # Intermediate state — fetch more
            await self._get_difference()

        elif isinstance(diff, raw.types.updates.DifferenceTooLong):
            self._pts_box.state = diff.pts
            await self._save_state()
            await self._get_difference()

    async def _apply_full_difference(
        self,
        diff: raw.types.updates.Difference | raw.types.updates.DifferenceSlice,
    ) -> None:
        await self._config.on_peers(diff.users, diff.chats)
        users = {u.id: u for u in diff.users}
        chats = {c.id: c for c in diff.chats}

        # Deliver new_messages as synthetic UpdateNewMessage
        for msg in diff.new_messages:
            self._config.on_update(
                raw.types.UpdateNewMessage(message=msg, pts=-1, pts_count=-1),
                users,
                chats,
            )

        # Deliver other_updates through normal routing (but bypass seq box)
        for update in diff.other_updates:
            utype = get_update_type(update)
            if utype == UPDATE_TYPE_CHANNEL:
                channel_id = get_update_channel_id(update)
                if channel_id:
                    await self._feed_channel(
                        channel_id,
                        PendingUpdate(
                            update=update,
                            pts=get_update_pts(update),
                            pts_count=get_update_pts_count(update),
                            users=users,
                            chats=chats,
                        ),
                    )
            else:
                self._config.on_update(update, users, chats)

        new_state = diff.state
        drained_pts = self._pts_box.apply_difference(new_state.pts)
        drained_qts = self._qts_box.apply_difference(new_state.qts)
        self._seq_box.apply_difference(new_state.seq)
        self._date = new_state.date

        for r in drained_pts + drained_qts:
            self._deliver(r)

        await self._save_state()

    async def _get_channel_difference(self, channel_id: int) -> None:
        state = self._channels.get(channel_id)
        if state is None:
            return

        diff_limit = self._config.diff_limit_bot if self._is_bot else self._config.diff_limit

        try:
            diff = await self._config.invoke(
                raw.functions.updates.GetChannelDifference(
                    channel=raw.types.InputChannel(
                        channel_id=channel_id,
                        access_hash=state.access_hash,
                    ),
                    filter=raw.types.ChannelMessagesFilterEmpty(),
                    pts=state.pts,
                    limit=diff_limit,
                ),
                60.0,
            )
        except Exception as e:
            log.warning("getChannelDifference for %d failed: %s", channel_id, e)
            return

        if isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
            state.set_pts(diff.pts)
            await self._config.set_channel_pts(channel_id, diff.pts)

        elif isinstance(diff, raw.types.updates.ChannelDifference):
            await self._config.on_peers(diff.users, diff.chats)
            users = {u.id: u for u in diff.users}
            chats = {c.id: c for c in diff.chats}
            for msg in diff.new_messages:
                self._config.on_update(
                    raw.types.UpdateNewMessage(message=msg, pts=-1, pts_count=-1),
                    users, chats,
                )
            for update in diff.other_updates:
                self._config.on_update(update, users, chats)
            drained = state.apply_difference(diff.pts)
            for r in drained:
                self._deliver(r)
            await self._config.set_channel_pts(channel_id, diff.pts)
            if not diff.final:
                await self._get_channel_difference(channel_id)

        elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
            new_pts = diff.dialog.pts
            state.set_pts(new_pts)
            await self._config.set_channel_pts(channel_id, new_pts)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _deliver(self, pending: PendingUpdate) -> None:
        # Skip synthetic getDifference updates (pts=-1)
        if pending.pts == -1:
            return
        self._config.on_update(pending.update, pending.users, pending.chats)

    async def _save_state(self) -> None:
        await self._config.set_state(
            self._pts_box.state,
            self._qts_box.state,
            self._seq_box.state,
            self._date,
        )
