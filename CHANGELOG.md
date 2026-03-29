# Changelog

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
