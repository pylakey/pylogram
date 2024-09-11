import typing

import pylogram

Client = typing.TypeVar("Client", bound="pylogram.Client", covariant=True)
Update = typing.TypeVar("Update", bound="pylogram.types.Update", covariant=True)
HandlerCallable: typing.TypeAlias = typing.Callable[
    [Client, Update],
    typing.Coroutine[typing.Any, typing.Any, typing.Any],
]
HandlerDecorator = typing.Callable[[HandlerCallable], HandlerCallable]
Filter = typing.TypeVar("Filter", bound="pylogram.filters.Filter", covariant=True)
FilterCallable = typing.Callable[[Filter, Client, Update], typing.Coroutine[typing.Any, typing.Any, bool]]
ProgressCallable = typing.Callable[[int | float, int | float], typing.Coroutine[typing.Any, typing.Any, typing.Any]]
RawHandlerCallable: typing.TypeAlias = typing.Callable[
    [
        Client,
        "pylogram.raw.base.Update",
        dict[int, "pylogram.raw.base.User"],
        dict[int, "pylogram.raw.base.Chat"],
    ],
    typing.Coroutine[typing.Any, typing.Any, typing.Any],
]
RawHandlerDecorator = typing.Callable[[RawHandlerCallable], RawHandlerCallable]
