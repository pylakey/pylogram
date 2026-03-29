import pylogram
from pylogram.invoke_middleware import Middleware


class AddInvokeMiddleware:
    def add_invoke_middleware(
        self: "pylogram.Client",
        middleware: Middleware,
    ) -> Middleware:
        """Register a request invoke middleware.

        Invoke middlewares wrap outgoing Telegram API calls, allowing you to
        intercept, modify, retry, or log requests and responses.

        A middleware is a callable ``(next_call) -> invoker`` where both
        *next_call* and the returned *invoker* have the signature
        ``async (query, timeout) -> result``.

        Parameters:
            middleware (:obj:`~pylogram.invoke_middleware.Middleware`):
                The middleware to register.

        Returns:
            The registered middleware (for decorator chaining).

        Example:
            .. code-block:: python

                from pylogram import Client
                from pylogram.invoke_middleware import FloodWaitHandler

                app = Client("my_account")
                app.add_invoke_middleware(FloodWaitHandler(sleep_threshold=30))
        """
        if self._invoke_middlewares is None:
            from pylogram.invoke_middleware import FloodWaitHandler, RetryHandler
            from pylogram.session import Session

            self._invoke_middlewares = [
                FloodWaitHandler(sleep_threshold=self.sleep_threshold),
                RetryHandler(max_retries=Session.MAX_RETRIES),
            ]
        self._invoke_middlewares.append(middleware)
        if self.is_connected:
            self._build_invoker()
        else:
            self._invoker = None
        return middleware
