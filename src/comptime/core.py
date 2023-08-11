"""
Contains core functionality used by the end developer.
"""

import os
from typing import Any, Callable, Iterable, ParamSpec, TypeVar, cast, overload

from .types import AnyCallable, Registration, RegistrationsDict

P = ParamSpec("P")
R = TypeVar("R")

ENV_KEY = "ITS_COMPTIME"
IS_COMPTIME_CONTEXT = os.getenv("ITS_COMPTIME") == "1"

T_noop = Callable[..., None]


def noop(*_: Any, **__: Any) -> None:
    """
    Do nothing: used by comptime.skip when running in comptime context.

    Not used in runtime context!
    """
    return None


class Skip:
    """
    Decorator class for 'comptime.skip'.
    """

    @overload
    def __call__(self, f: None = None) -> "Skip":
        ...

    @overload
    def __call__(self, f: Callable[P, R]) -> Callable[P, R]:
        ...

    def __call__(self, f: Callable[P, R] = None) -> Callable[P, R] | "Skip":
        """
        Called when `skip` is used as a decorator.

        Can be used both as @skip or @skip().
        """
        if not f:
            return skip

        if IS_COMPTIME_CONTEXT:
            return cast(Callable[P, R], noop)

        return f


skip = Skip()

registrations: RegistrationsDict = {}


class Comptime:
    """
    Class used to store registrations.
    """

    @staticmethod
    def get_registrations() -> RegistrationsDict:
        """
        Expose 'registrations' variable.

        (for when you have access to comptime but don't want to import from comptime.core)
        """
        return registrations

    @staticmethod
    def register(func: AnyCallable, args: Iterable[Any] = ()) -> None:
        """
        Register a new function to be executed at compile time.
        """
        registrations[func.__name__] = Registration(func.__name__, func, tuple(args))

    @staticmethod
    @overload
    def skip(f: None = None) -> Skip:
        return skip(f)

    @staticmethod
    @overload
    def skip(f: Callable[P, R]) -> Callable[P, R]:
        return skip(f)

    @staticmethod
    def skip(f: Callable[P, R] = None) -> Callable[P, R] | Skip:
        """
        Alias so you can use comptime.skip even if you imported `comptime from comptime`.
        """
        return skip(f)

    @overload
    def __call__(self, wrapped: None = None, *args: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
        ...

    @overload
    def __call__(self, wrapped: Callable[P, R], *args: Any) -> Callable[P, R]:
        ...

    def __call__(
        self, wrapped: Callable[P, R] = None, *args: Any
    ) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Using a class with __call__ works a bit better than simply a function: we have access to instance variables now.

        Can be used as @comptime or @comptime().
        The latter supports adding arguments that will be passed to the function when pre-copmuting.
        """
        if callable(wrapped):
            self.register(wrapped)
            return wrapped

        def inner(func: Callable[P, R]) -> Callable[P, R]:
            self.register(func, [wrapped, *args])
            return func

        return inner


comptime = Comptime()
