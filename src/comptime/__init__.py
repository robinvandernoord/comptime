"""
This file exposes certain functions to the library.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT

from .core import comptime, skip

__all__ = [
    "comptime",
    "skip",
]
