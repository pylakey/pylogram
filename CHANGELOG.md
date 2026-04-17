# Changelog

## 0.16.2

### Fixed

- `UpdatesManager._apply_full_difference` now reads `intermediate_state` from `updates.differenceSlice` instead of the non-existent `state` attribute, preventing an `AttributeError` during first-sync `getDifference` when the server returns a sliced response.

## 0.16.1

### Added

- `utils.get_dialog_message_key` helper, shared between `get_dialogs` and `raw_parsers` for consistent dialog message keying.

### Fixed

- `UpdatesManager` now reads `pts` from `diff.dialog.pts` in the `ChannelDifferenceTooLong` branch, correcting channel state recovery when the server reports a too-long channel diff.

## 0.16.0

### Added

- `ConnectionParams` — typed dataclass serialised to a TL `JsonObject`, covering the six Android-client `initConnection.params` keys (`device_token`, `data`, `installer`, `package_id`, `tz_offset`, `perf_cat`). Passed via the `Client` constructor and wired through `Session.start()` into `InitConnection`.

## 0.15.0

### Added

- **Update gap recovery** — full pts/qts/seq sequence tracking with automatic gap detection and recovery via `getDifference`.
  - New `pylogram/updates/` package: `UpdatesManager`, `SequenceBox`, `GapBuffer`, `ChannelState`.
  - Matches official Telegram Android client behaviour (1500ms gap timeout, peer-check on short updates).
  - Per-channel `asyncio.Task` with lazy creation and configurable idle cleanup.
  - Idle timeout (default 15 min) triggers `getDifference` as a safety net.
  - `UpdatesConfig` — all tuning knobs: `gap_timeout`, `idle_timeout`, `diff_limit`, etc.
  - `Client(updates_config=UpdatesConfig(...))` — opt-in customisation; auto-wired by default.
  - `UpdatesConfig(enabled=False)` — passthrough mode preserving previous behaviour.

### Changed

- `UpdatesTooLong` now triggers `getDifference` instead of being silently logged.
- `UpdateShortMessage` / `UpdateShortChatMessage` now synthesised from peer cache instead of always calling `getDifference`.
- `updates_watchdog` removed — replaced by `idle_timeout` in `UpdatesManager`.
- Storage schema bumped to version 4: new `update_state` and `channel_pts` tables (auto-migrated).

## 0.14.0

### Added

- **Invoke middleware system** — composable middleware chain for outgoing Telegram API requests (`Client.invoke()`).
  - `Invoker` and `Middleware` type aliases for building custom middleware.
  - `chain()` function to compose middleware around a terminal invoker.
  - `FloodWaitHandler` — automatic sleep and retry on `FloodWait` errors (replaces hardcoded logic).
  - `RetryHandler` — automatic retry on transient errors (`OSError`, `InternalServerError`, `ServiceUnavailable`).
  - `Client(invoke_middlewares=[...])` — configure middleware via constructor.
  - `Client.add_invoke_middleware()` / `Client.remove_invoke_middleware()` — runtime registration.
  - `@Client.on_invoke()` — decorator for registering middleware.
  - Per-call `sleep_threshold` and `retries` overrides continue to work transparently.

### Changed

- `FloodWaitHandler` and `RetryHandler` are now the **default middleware** — existing behavior is fully preserved with zero breaking changes.
- `update_storage_peers` is now called inside the terminal invoker, guaranteeing peer updates regardless of middleware errors.

## 0.13.0

- Update TL schema to layer 223.
- Remove tox.ini, superseded by uv run.
- Move dev dependencies to pyproject.toml.
