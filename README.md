# comptime

<div align="center">
    <a href="https://pypi.org/project/comptime"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/comptime.svg"/></a>
    <a href="https://pypi.org/project/comptime"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/comptime.svg"/></a>
    <br/>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
    <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"/></a>
    <br/>
    <a href="https://github.com/robinvandernoord/comptime/actions"><img alt="comptime checks" src="https://github.com/robinvandernoord/comptime/actions/workflows/comptime.yml/badge.svg?branch=development"/></a>
    <a href="https://github.com/robinvandernoord/comptime/actions"><img alt="Coverage" src="coverage.svg"/></a>
</div>

"Comptime" accelerates Python code by precomputing complex calculations, turning them into simple lookups for faster
execution.

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

Comptime is inspired by the concept of compile-time computation found in languages
like [Zig](https://ziglang.org/documentation/master/#comptime), and it brings this powerful
feature into the world of Python, an interpreted language. By utilizing special decorators, you can mark functions whose
return values should be precomputed. This enables you to separate computationally expensive parts of your code,
performing those calculations once, and embedding the results directly into your source code. The result is Python code
that executes faster by turning complex calculations into simple lookups. Whether you're optimizing critical performance
bottlenecks or exploring new ways to structure your code, Comptime offers a novel approach to accelerate your Python
development.

**"Zig into Python's speed lane with Comptime – it's not a sprint; it's a compile!"**

## :warning: Warning: this is only a proof-of-concept

This code was only created to test the concept. It should NOT be used in a production environment, as I can not
guarantee at this time that the semantics of the outputted code are correct.
Furthermore, initial performance tests show that for relatively simple calculations, this does NOT actually improve
performance:

```bash
python examples/perf.py # pre-comptime:
# Function executed in: 2.0992 seconds total; avg of 209.92 ns. per execution.
python examples/perf_match.py # comptime with match-case strategy:
# Function executed in: 21.5824 seconds total; avg of 2158.24 ns. per execution.
python examples/perf_dict.py # comptime with dict lookup strategy:
# Function executed in: 152.4098 seconds total; avg of 15240.98 ns. per execution.
```

While this package could be useful in cases where the calculation is actually heavy, it could also negatively impact
your performance!

## Installation

```console
pip install comptime
```

## Usage

```python
# src_raw/main.py: before comptime
from comptime import comptime


@comptime.skip
def nonpure_method():
    # this method has side effects so should only be used at runtime
    print("e.g. sending an email")


@comptime
def my_method():
    ...
    # some expensive calculations
    nonpure_method()  # not executed due to @comptime.skip
    return 41 + 1


@comptime("users", "posts")
def call_api(endpoint):
    # api get value for endpoint
    ...
    return value


call_api("other")  # possible comptime warning due to unsupported argument?
```

```bash
comptime --input src_raw --output src_compiled
```

```python
# src_compiled/main.py: after comptime
import typing


def nonpure_method():
    # this method has side effects so should only be used at runtime
    print("e.g. sending an email")


def my_method():
    # computed by comptime 
    return 42


def call_api(endpoint: typing.Literal["users", "posts"]):
    # computed by comptime
    match endpoint:
        case "users":
            return ['user1']
        case "posts":
            return ['post1']
        case _:
            raise ValueError("Uncompiled variant {endpoint}")
    return value
```

## Acknowledgments

This project owes its inspiration and certain elements of its design to various sources:

- **Zig Programming Language:** The concept of compile-time computation in Comptime is inspired
  by [Zig](https://github.com/ziglang/zig), a language that emphasizes safety, performance, and readability. A special
  thank you to Zig's creators and community for their innovative approach to programming.

- **GPT-4 by OpenAI:** Assistance with the project boilerplate, creative brainstorming, and crafting the memorable
  slogan "Zig into Python's speed lane with Comptime – it's not a sprint; it's a compile!" was provided by GPT-4. It
  also wrote this section.

Please note that the author of comptime is not affiliated with Zig, OpenAI, or any other entities mentioned
above. The acknowledgments are expressions of gratitude and inspiration and do not imply any formal association or
endorsement by these parties.

## License

`comptime` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
