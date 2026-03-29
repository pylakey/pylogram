import pylogram
from pylogram.invoke_middleware import Middleware


class RemoveInvokeMiddleware:
    def remove_invoke_middleware(
        self: "pylogram.Client",
        middleware: Middleware,
    ) -> None:
        """Remove a previously registered invoke middleware.

        Parameters:
            middleware (:obj:`~pylogram.invoke_middleware.Middleware`):
                The middleware to remove.

        Raises:
            ValueError: If the middleware is not registered or only defaults are active.
        """
        if self._invoke_middlewares is None:
            raise ValueError("No custom invoke middlewares registered")
        self._invoke_middlewares.remove(middleware)
        if self.is_connected:
            self._build_invoker()
        else:
            self._invoker = None
