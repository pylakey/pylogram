"""Integration tests for UpdatesManager using mock callbacks."""
from __future__ import annotations

import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock

from pylogram import raw
from pylogram.updates.manager import UpdatesManager
from pylogram.updates.types import UpdatesConfig


def _make_config(**kwargs) -> UpdatesConfig:
    """Build an UpdatesConfig wired to simple in-memory state."""
    state: dict = {"pts": 0, "qts": 0, "seq": 0, "date": 0}
    channel_pts: dict[int, int] = {}
    delivered: list = []

    defaults = dict(
        on_update=lambda u, users, chats: delivered.append((u, users, chats)),
        on_peers=AsyncMock(return_value=None),
        invoke=AsyncMock(),
        get_channel_access_hash=AsyncMock(return_value=12345),
        get_peer=AsyncMock(return_value=MagicMock()),
        get_my_user_id=AsyncMock(return_value=1),
        get_state=AsyncMock(return_value=None),
        set_state=AsyncMock(),
        get_channel_pts=AsyncMock(side_effect=lambda cid: channel_pts.get(cid)),
        set_channel_pts=AsyncMock(side_effect=lambda cid, pts: channel_pts.update({cid: pts})),
        gap_timeout=0.05,     # fast for tests
        idle_timeout=9999.0,  # don't fire during tests
        channel_idle_timeout=9999.0,
    )
    defaults.update(kwargs)
    cfg = UpdatesConfig(**defaults)
    cfg._delivered = delivered
    return cfg


@pytest.mark.asyncio
async def test_fresh_start_calls_get_state():
    """On first start (no persisted state), UpdatesManager calls updates.GetState."""
    state_result = MagicMock()
    state_result.pts = 100
    state_result.qts = 0
    state_result.seq = 5
    state_result.date = 1000000

    cfg = _make_config()
    cfg.invoke = AsyncMock(return_value=state_result)
    cfg.get_state = AsyncMock(return_value=None)

    manager = UpdatesManager(cfg)
    await manager.start()
    await manager.stop()

    # Should have invoked updates.GetState
    call_args = cfg.invoke.call_args_list
    assert any(
        isinstance(a[0][0], raw.functions.updates.GetState)
        for a in call_args
    )


@pytest.mark.asyncio
async def test_in_order_update_delivered_immediately():
    """An update with pts = localState+1 is delivered without buffering."""
    state_result = MagicMock(pts=100, qts=0, seq=0, date=0)
    cfg = _make_config(invoke=AsyncMock(return_value=state_result))

    manager = UpdatesManager(cfg)
    await manager.start()

    update = raw.types.UpdateNewMessage(
        message=raw.types.MessageEmpty(id=1),
        pts=101,
        pts_count=1,
    )
    container = raw.types.Updates(
        updates=[update],
        users=[],
        chats=[],
        date=0,
        seq=0,
    )
    await manager.handle(container)
    await asyncio.sleep(0.01)  # let manager process

    await manager.stop()
    assert len(cfg._delivered) == 1
    assert cfg._delivered[0][0] is update


@pytest.mark.asyncio
async def test_duplicate_update_not_delivered():
    """An update with pts <= localState is silently dropped."""
    state_result = MagicMock(pts=100, qts=0, seq=0, date=0)
    cfg = _make_config(invoke=AsyncMock(return_value=state_result))

    manager = UpdatesManager(cfg)
    await manager.start()

    # pts=100, count=1 → start=99; local is 100, so local+count(1)=101 > 100 → ignore
    update = raw.types.UpdateNewMessage(
        message=raw.types.MessageEmpty(id=1),
        pts=100,
        pts_count=1,
    )
    container = raw.types.Updates(
        updates=[update], users=[], chats=[], date=0, seq=0,
    )
    await manager.handle(container)
    await asyncio.sleep(0.01)

    await manager.stop()
    assert len(cfg._delivered) == 0


@pytest.mark.asyncio
async def test_gap_triggers_get_difference_after_timeout():
    """A gap in pts causes getDifference after gap_timeout."""
    state_result = MagicMock(pts=100, qts=0, seq=0, date=0)
    diff_result = raw.types.updates.DifferenceEmpty(date=0, seq=0)

    invoke_results = [state_result, diff_result]
    invoke_mock = AsyncMock(side_effect=invoke_results)
    cfg = _make_config(invoke=invoke_mock)

    manager = UpdatesManager(cfg)
    await manager.start()

    # pts=105, count=2 — gap at [100, 103)
    update = raw.types.UpdateNewMessage(
        message=raw.types.MessageEmpty(id=1),
        pts=105,
        pts_count=2,
    )
    container = raw.types.Updates(
        updates=[update], users=[], chats=[], date=0, seq=0,
    )
    await manager.handle(container)
    await asyncio.sleep(0.2)  # wait for gap_timeout (0.05s) + margin

    await manager.stop()

    # getDifference should have been called
    calls = invoke_mock.call_args_list
    diff_calls = [
        c for c in calls
        if isinstance(c[0][0], raw.functions.updates.GetDifference)
    ]
    assert len(diff_calls) >= 1


@pytest.mark.asyncio
async def test_get_difference_applies_slice_intermediate_state():
    """Regression: DifferenceSlice exposes `intermediate_state`, not `state`."""
    slice_result = raw.types.updates.DifferenceSlice(
        new_messages=[],
        new_encrypted_messages=[],
        other_updates=[],
        chats=[],
        users=[],
        intermediate_state=raw.types.updates.State(
            pts=150, qts=0, date=1500, seq=0, unread_count=0,
        ),
    )
    empty_result = raw.types.updates.DifferenceEmpty(date=1500, seq=0)

    invoke_mock = AsyncMock(side_effect=[slice_result, empty_result])
    cfg = _make_config(
        invoke=invoke_mock,
        get_state=AsyncMock(return_value=(100, 0, 0, 1000)),
    )

    manager = UpdatesManager(cfg)
    await manager.start()
    await manager.stop()

    assert manager._pts_box.state == 150
    diff_calls = [
        c for c in invoke_mock.call_args_list
        if isinstance(c[0][0], raw.functions.updates.GetDifference)
    ]
    assert len(diff_calls) == 2


@pytest.mark.asyncio
async def test_updates_too_long_triggers_get_difference():
    """UpdatesTooLong immediately triggers getDifference."""
    state_result = MagicMock(pts=100, qts=0, seq=0, date=0)
    diff_result = raw.types.updates.DifferenceEmpty(date=0, seq=0)

    invoke_mock = AsyncMock(side_effect=[state_result, diff_result])
    cfg = _make_config(invoke=invoke_mock)

    manager = UpdatesManager(cfg)
    await manager.start()
    await manager.handle(raw.types.UpdatesTooLong())
    await asyncio.sleep(0.05)

    await manager.stop()

    calls = invoke_mock.call_args_list
    diff_calls = [
        c for c in calls
        if isinstance(c[0][0], raw.functions.updates.GetDifference)
    ]
    assert len(diff_calls) >= 1
