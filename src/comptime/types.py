"""
Contains useful types for this project.
"""

import typing
from typing import Any, Callable, NamedTuple, TypeVar

T = TypeVar("T")

AnyCallable = Callable[..., Any]
DynamicTuple: typing.TypeAlias = tuple[T, ...]


class Registration(NamedTuple):
    """
    A registration of a function decorated with @comptime.
    """

    name: str
    func: AnyCallable
    args: DynamicTuple[Any]


RegistrationsDict = dict[str, Registration]

ResultsDictKey = str | tuple[str, typing.Any | tuple[typing.Any, ...]]
ResultsDictValue = typing.Any
ResultsDictType = dict[ResultsDictKey, ResultsDictValue]
