#!/usr/bin/env python3
from datetime import timedelta
from itertools import chain
from pathlib import Path
from argparse import ArgumentParser
from typing import Iterator, Iterable

import numpy as np
from matplotlib import pyplot
import adapters.bepost
from numpy.polynomial import polynomial


def trend(dates, cumulative, label):
    dates_u = unix_timestamps(dates)
    p = polynomial.polyfit(dates_u, cumulative, 1)
    line = np.poly1d(p)
    edges, edges_u = find_edges(dates)
    return (edges, line(edges_u)), f'{label}-trend: {line}'


def find_edges(dates):
    edges = (min(dates), max(dates) + timedelta(weeks=30))
    edges_u = tuple(map(lambda d: d.timestamp(), edges))
    return edges, edges_u


def unix_timestamps(dates):
    dates_t = np.empty(len(dates))
    for i, d in enumerate(dates):
        dates_t[i] = d.timestamp()
    return dates_t


def plot(dates, numbers):
    cumulative = np.cumsum(numbers)
    pyplot.plot_date(dates, numbers, label='transacties')
    pyplot.plot_date(dates, cumulative, label='saldo')
    pyplot.legend()


def read_lines(filename: str) -> Iterator[str]:
    with Path(filename).open() as f:
        return f.readlines()


def main():
    parser = ArgumentParser()
    parser.add_argument('data_path', type=str, nargs='*')
    options = parser.parse_args()

    line_lists = map(read_lines, options.data_path)
    transaction_lists = map(adapters.bepost.from_lines, line_lists)

    transactions = sorted(
        chain(*transaction_lists),
        key=lambda t: t.date,
        reverse=True)

    dates = tuple(t.date for t in transactions)
    numbers = tuple(t.amount for t in transactions)
    plot(dates, numbers)
    pyplot.show()


main()
