import pylogram
from pylogram.invoke_middleware import Middleware


class InvokeMiddleware:
    def on_invoke(self: "pylogram.Client") -> Middleware:
        """Decorator for registering an invoke middleware.

        This does the same thing as :meth:`~pylogram.Client.add_invoke_middleware`.

        Example:
            .. code-block:: python

                from pylogram import Client

                app = Client("my_account")

                @app.on_invoke()
                def logging_middleware(next_call):
                    async def invoke(query, timeout):
                        print(f"Calling {query.QUALNAME}")
                        result = await next_call(query, timeout)
                        print(f"Got response for {query.QUALNAME}")
                        return result
                    return invoke
        """
        def decorator(func: Middleware) -> Middleware:
            self.add_invoke_middleware(func)
            return func
        return decorator
