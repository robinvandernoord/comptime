import typing

# from .secondary import add
from secondary import add


def side_effect(arg):
    # this has a side effect.
    print("SIDE-EFFECT", arg)


def side_effect2():
    # this has a side effect too
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
    return {
        "first": "1",
        "second": "114813069527425452423283320117768198402231770208869520047764273682576626139237031385665948631650626991844596463898746277344711896086305533142593135616665318539129989145312280000688779148240044871428926990063486244781615463646388363947317026040466353970904996558162398808944629605623311649536164221970332681344168908984458505602379484807914058900934776500429002716706625830522008132236281291761267883317206598995396418127021779858404042159853183251540889433902091920554957783589672039160081957216630582755380425583726015528348786419432054508915275783882625175435528800822842770817965453762184851149029376",
    }[arg1]


def multiple1(
    string: typing.Literal["value2", "value1"], number: typing.Literal[2,]
) -> str:
    return {("value1", 2): "value1value1", ("value2", 2): "value2value2"}[
        string, number
    ]


def multiple2(string: typing.Literal["value2", "value1"], verbose: bool) -> str:
    return {
        ("value1", True): "value1",
        ("value1", False): "",
        ("value2", True): "value2",
        ("value2", False): "",
    }[string, verbose]


def main():
    print("Don't touch this code!")
    side_effect("main")
    print(expensive_computation())
    print(multiple1("value1", 2))
    print(multiple2("value1", False))
    print(with_predefined_arg("first"))
    print(with_predefined_arg("third"))  # -> ValueError


if __name__ == "__main__":
    main()

