from __future__ import annotations

import asyncio
import contextvars
import logging
from collections.abc import Awaitable, Callable
from typing import TypeAlias

from pylogram.raw.core import TLObject

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

Invoker: TypeAlias = Callable[[TLObject, float], Awaitable[TLObject]]
"""Async callable that sends a TL query and returns the response.

Signature: ``async (query: TLObject, timeout: float) -> TLObject``
"""

Middleware: TypeAlias = Callable[[Invoker], Invoker]
"""Transforms an Invoker into a new Invoker, wrapping the call.

Signature: ``(next_call: Invoker) -> Invoker``
"""


# ---------------------------------------------------------------------------
# Invoke context (per-call overrides via contextvars)
# ---------------------------------------------------------------------------

_sleep_threshold_var: contextvars.ContextVar[float | None] = contextvars.ContextVar(
    "invoke_sleep_threshold", default=None,
)
_max_retries_var: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "invoke_max_retries", default=None,
)


def get_sleep_threshold() -> float | None:
    """Return per-call sleep_threshold override, or None for default."""
    return _sleep_threshold_var.get()


def get_max_retries() -> int | None:
    """Return per-call max_retries override, or None for default."""
    return _max_retries_var.get()


# ---------------------------------------------------------------------------
# Chain builder
# ---------------------------------------------------------------------------

def chain(invoker: Invoker, *middlewares: Middleware) -> Invoker:
    """Build a middleware chain around a terminal invoker.

    Middlewares execute in registration order (first registered = outermost).
    Each middleware wraps the next one, capturing ``next_call`` in a closure.
    """
    for mw in reversed(middlewares):
        invoker = mw(invoker)
    return invoker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _query_name(query: TLObject) -> str:
    """Extract a human-readable query name, unwrapping InvokeWith* layers."""
    while hasattr(query, "query") and hasattr(type(query), "QUALNAME"):
        name = type(query).__name__
        if name.startswith("InvokeWith") or name.startswith("InvokeAfter"):
            query = query.query
        else:
            break
    return ".".join(query.QUALNAME.split(".")[1:])


# ---------------------------------------------------------------------------
# Built-in middleware
# ---------------------------------------------------------------------------

class FloodWaitHandler:
    """Automatically sleeps and retries requests on FloodWait errors.

    When a ``FloodWait`` error is received and the wait duration does not
    exceed *sleep_threshold*, the middleware sleeps for the required duration
    and transparently retries the request.  If the wait exceeds the threshold
    (or the threshold is negative), the error is re-raised to the caller.

    The threshold can be overridden per-call via ``Client.invoke()``'s
    *sleep_threshold* parameter — the override is propagated through
    ``contextvars`` and takes precedence over the default.

    Parameters:
        sleep_threshold: Maximum number of seconds to wait automatically.
            Set to a negative value to always re-raise FloodWait.
            Defaults to ``10.0``.
    """

    def __init__(self, sleep_threshold: float = 10.0) -> None:
        self.sleep_threshold = sleep_threshold

    def __call__(self, next_call: Invoker) -> Invoker:
        from pylogram.errors import FloodWait

        default_threshold = self.sleep_threshold

        async def invoke(query: TLObject, timeout: float) -> TLObject:
            threshold = get_sleep_threshold()
            if threshold is None:
                threshold = default_threshold

            while True:
                try:
                    return await next_call(query, timeout)
                except FloodWait as e:
                    amount = e.value

                    if amount > threshold >= 0:
                        raise

                    log.warning(
                        'Sleeping %s seconds (flood wait for "%s")',
                        amount,
                        _query_name(query),
                    )

                    await asyncio.sleep(amount)

        return invoke


class RetryHandler:
    """Retries requests on transient errors with constant backoff.

    Handles ``OSError``, ``InternalServerError``, and ``ServiceUnavailable``
    by retrying up to *max_retries* times with a fixed *backoff* delay
    between attempts.

    The retry count can be overridden per-call via ``contextvars``
    (see :func:`get_max_retries`).

    Parameters:
        max_retries: Maximum number of retry attempts.  Defaults to ``10``.
        backoff: Delay in seconds between retries.  Defaults to ``0.5``.
    """

    def __init__(self, max_retries: int = 10, backoff: float = 0.5) -> None:
        self.max_retries = max_retries
        self.backoff = backoff

    def __call__(self, next_call: Invoker) -> Invoker:
        from pylogram.errors import InternalServerError, ServiceUnavailable

        default_retries = self.max_retries
        backoff = self.backoff

        async def invoke(query: TLObject, timeout: float) -> TLObject:
            retries = get_max_retries()
            if retries is None:
                retries = default_retries

            for attempt in range(retries + 1):
                try:
                    return await next_call(query, timeout)
                except (OSError, InternalServerError, ServiceUnavailable) as e:
                    if attempt == retries:
                        raise e from None

                    remaining = retries - attempt - 1
                    (log.warning if remaining < 1 else log.info)(
                        '[%s] Retrying "%s" due to: %s',
                        attempt + 1,
                        _query_name(query),
                        str(e) or repr(e),
                    )

                    await asyncio.sleep(backoff)

        return invoke
