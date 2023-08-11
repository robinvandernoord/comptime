import typing
from secondary import add


def side_effect(arg):
    print("SIDE-EFFECT", arg)


def side_effect2():
    print("SIDE-EFFECT", "second side effect")


def expensive_computation() -> int:
    """
    Really expensive
    """
    return 5


def with_predefined_arg(arg1: typing.Literal["second", "first"]) -> str:
    """
    Amazing!
    """
    match arg1:
        case "first":
            return "1"
        case "second":
            return "2"
        case _:
            raise ValueError(f"Uncompiled variant arg1={arg1}")


def multiple1(
    string: typing.Literal["value1", "value2"], number: typing.Literal[2,]
) -> str:
    match (string, number):
        case ("value1", 2):
            return "value1value1"
        case ("value2", 2):
            return "value2value2"
        case _:
            raise ValueError(f"Uncompiled variant string={string} number={number}")


def multiple2(string: typing.Literal["value1", "value2"], verbose: bool) -> str:
    match (string, verbose):
        case ("value1", True):
            return "value1"
        case ("value1", False):
            return ""
        case ("value2", True):
            return "value2"
        case ("value2", False):
            return ""
        case _:
            raise ValueError(f"Uncompiled variant string={string} verbose={verbose}")


def main():
    print("Don't touch this code!")
    side_effect("main")
    print(expensive_computation())
    print(with_predefined_arg("first"))
    print(with_predefined_arg("third"))


if __name__ == "__main__":
    main()

