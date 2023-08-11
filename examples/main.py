from comptime import comptime
from .secondary import add


# from secondary import add


@comptime
def expensive_computation():
    return add(2, 3)


@comptime("first", "second")
def with_predefined_arg(arg1):
    if arg1 == "first":
        return "1"
    else:
        return "2"


def main():
    print("Don't touch this code!")
    print(expensive_computation())

    print(with_predefined_arg("first"))

    print(with_predefined_arg("third"))  # -> ValueError


if __name__ == "__main__":
    main()
