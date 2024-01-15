from __future__ import annotations

from typing import (
    Any,
    Callable,
    Coroutine,
)

CallNextMiddlewareCallable = Callable[['pylogram.Client', 'pylogram.types.Update'], Coroutine[Any, Any, Any]]
Middleware = Callable[['pylogram.Client', 'pylogram.types.Update', CallNextMiddlewareCallable], Coroutine[Any, Any, Any]]
