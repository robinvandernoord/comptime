from comptime import comptime

# from .secondary import add
from secondary import add


@comptime.skip
def side_effect(arg):
    # this has a side effect.
    print("SIDE-EFFECT", arg)


@comptime.skip()
def side_effect2():
    # this has a side effect too
    print("SIDE-EFFECT", "second side effect")


@comptime
def expensive_computation() -> int:
    """
    Really expensive
    """
    # DONT RUN THESE TWO AT COMPTIME: !!
    side_effect("expensive_computation")
    side_effect2()
    return add(2, 3)


@comptime("first", "second")
def with_predefined_arg(arg1) -> str:
    """
    Amazing!
    """
    side_effect("with_predefined_arg")

    if arg1 == "first":
        return str(1 ** 1000)
    else:
        return str(2 ** 2000)


@comptime(("value1", "value2"), 2)
def multiple1(string: str, number: int) -> str:
    return string * number


@comptime(("value1", "value2"), (True, False))
def multiple2(string: str, verbose: bool) -> str:
    return string if verbose else ""


def main():
    print("Don't touch this code!")
    side_effect("main")
    print(expensive_computation())

    print(
        multiple1("value1", 2)
    )

    print(
        multiple2("value1", False)
    )

    print(with_predefined_arg("first"))

    print(with_predefined_arg("third"))  # -> ValueError


if __name__ == "__main__":
    main()
