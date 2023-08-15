import timeit

from comptime import comptime
import math
import random


def sine_value(angle):
    return math.sin(math.radians(angle))


@comptime(*range(361))
def precomputed_sine(angle):
    return sine_value(angle)


def main():
    n = 1000_000

    random_args = [
        random.randint(0, 360)
        for _
        in range(n)
    ]

    def run_a_lot():
        for i in range(n):
            precomputed_sine(
                random_args[i]
            )

    n2 = 10 # better than making 'n' bigger because that takes more memory
    time_taken = timeit.timeit(run_a_lot, number=n2)
    per_run = (time_taken / n / n2) * 1e9
    print(f"Function executed in: {time_taken:.4f} seconds total; avg of {per_run:.2f} ns. per execution.")


if __name__ == '__main__':
    main()
