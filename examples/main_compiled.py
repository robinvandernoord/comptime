import typing
from .secondary import add

# from secondary import add


def expensive_computation():
    return 5


def with_predefined_arg(arg1: typing.Literal["first", "second"]):
    match arg1:
        case "first":
            return "1"
        case "second":
            return "2"
        case _:
            raise ValueError(f"Uncompiled variant arg1={arg1}")


def main():
    print("Don't touch this code!")
    print(expensive_computation())
    print(with_predefined_arg("first"))
    print(with_predefined_arg("third"))  # -> ValueError


if __name__ == "__main__":
    main()
