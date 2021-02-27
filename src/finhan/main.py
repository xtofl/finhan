#!/usr/bin/env python3
from datetime import timedelta
from functools import reduce
from itertools import chain, starmap
from pathlib import Path
from argparse import ArgumentParser
from typing import Iterator, Iterable

import numpy as np
from matplotlib import pyplot
import finhan.adapters.bepost as bepost
from numpy.polynomial import polynomial

from finhan.account import read_balance


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


def plot(dates, numbers, account, current_balance):
    cumulative = np.cumsum(numbers) + (current_balance or 0)
    pyplot.plot_date(dates, numbers, label=account)
    pyplot.plot_date(dates, cumulative, '-+', label=f'saldo {account}')
    pyplot.legend()


def read_lines(filename: str) -> Iterator[str]:
    with Path(filename).open() as f:
        return f.readlines()


class Balance:
    '''convert cmdline argument to balance'''
    def __init__(self, b: str):
        return b.split(':')


def main():
    parser = ArgumentParser()
    parser.add_argument('data_path', type=str, nargs='*')
    parser.add_argument(
        '--balance', type=Path,
        help='Path to current balance file.  This file should contain a '
             'dict of account -> balance')

    options = parser.parse_args()

    line_lists = map(read_lines, options.data_path)
    transaction_lists = tuple(map(bepost.from_lines,
                                  line_lists))

    transaction_lists = tuple(
        starmap(
            lambda ts, account: (
                tuple(ts), account),
            transaction_lists
        )
    )

    accounts = tuple(account for _, account in transaction_lists)

    def for_account(account):
        return (t for t, a in transaction_lists if a == account)

    def join_transactions(t, other):
        return tuple(t) + tuple(other)

    transactions_by_account = {
        account: reduce(join_transactions, for_account(account), tuple())
        for account in accounts
    }
    current_balance = read_balance(options.balance)
    for account, transactions in transactions_by_account.items():
        plot_for_account(account,
                         current_balance.get(account, None),
                         transactions)
    pyplot.show()


def plot_for_account(account, current_balance, transactions):
    transactions = sorted(
                    transactions,
                    key=lambda t: t.date,
                    reverse=True)
    dates = tuple(t.date for t in transactions)
    numbers = tuple(t.amount for t in transactions)
    plot(
        dates, numbers,
        account,
        current_balance=current_balance)


main()
