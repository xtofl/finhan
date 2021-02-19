from pathlib import Path
from argparse import ArgumentParser
import numpy as np
from matplotlib import pyplot
from pandas import read_csv
import adapters.bepost


def plot(dates, numbers ):
    print(dates[:10])
    print(numbers[:10])
    return pyplot.plot_date(dates, numbers)


def main():
    parser = ArgumentParser()
    parser.add_argument('data_path', type=str)
    options = parser.parse_args()

    with Path(options.data_path).open() as f:
        transactions = tuple(adapters.bepost.from_lines(f.readlines()))
        dates = tuple(t.date for t in transactions)
        numbers = tuple(t.amount for t in transactions)
        plot(dates, numbers)
    pyplot.show()


main()
