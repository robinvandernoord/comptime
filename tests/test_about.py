from src.comptime.__about__ import __version__
import re


def test_about():
    version_re = re.compile(r"\d+\.\d+\.\d+.*")
    assert version_re.findall(__version__)
