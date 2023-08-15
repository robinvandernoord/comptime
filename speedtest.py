from pathlib import Path

from src.comptime.compiler import write

if __name__ == "__main__":
    base = Path(__file__).parent / "examples"

    write(base / "perf.py", strategy="match", output=base / "perf_match.py")
    write(base / "perf.py", strategy="dict", output=base / "perf_dict.py")
