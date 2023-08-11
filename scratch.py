from pathlib import Path

from src.comptime.compiler import write

if __name__ == "__main__":
    base = Path(__file__).parent / "examples"

    write(base / "main.py")
    write(base / "absolute.py", has_absolute_imports=True)
