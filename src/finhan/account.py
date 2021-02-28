from datetime import timedelta
from functools import reduce
from itertools import starmap, chain
from pathlib import Path
from typing import Dict, Iterator

import numpy as np
import yaml

from finhan.adapters import bepost as bepost

AccountId = str
Balance = float


def read_balance(filename: Path) -> Dict[AccountId, Balance]:
    with filename.open() as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    assert config['schema'] == 'v1'
    date = config['last updated']
    accounts = config['accounts']
    return {AccountId(a['id']): Balance(a['balance']) for a in accounts}


def read_account_transactions(data_paths):
    line_lists = map(read_lines, data_paths)
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
    return transactions_by_account


def find_edges(dates):
    edges = (min(dates), max(dates) + timedelta(weeks=30))
    edges_u = tuple(map(lambda d: d.timestamp(), edges))
    return edges, edges_u


def unix_timestamps(dates):
    dates_t = np.empty(len(dates))
    for i, d in enumerate(dates):
        dates_t[i] = d.timestamp()
    return dates_t


def apply_balance(current_balance, numbers):
    saldo_floating = np.cumsum(numbers)
    last_floating_saldo = saldo_floating[-1]
    saldo = saldo_floating + (current_balance - last_floating_saldo)
    return saldo


def dates_and_numbers(transactions):
    transactions = sorted(
        transactions,
        key=lambda t: t.date,
        reverse=True)
    dates = tuple(t.date for t in transactions)
    numbers = tuple(t.amount for t in transactions)
    return dates, numbers


def joint_account_transactions(current_balance, transactions_by_account):
    transactions_by_date = sorted(tuple(
        chain(*transactions_by_account.values())
    ), key=lambda t: t.date)
    all_transactions = np.fromiter(
        (t.amount for t in transactions_by_date),
        dtype=float
    )
    floating_grand_total = np.cumsum(all_transactions)
    last = floating_grand_total[-1]
    grand_current_balance = sum(current_balance.values())
    grand_total = floating_grand_total + (grand_current_balance - last)
    dates = tuple(t.date for t in transactions_by_date)
    return dates, grand_total


def read_lines(filename: str) -> Iterator[str]:
    with Path(filename).open() as f:
        return f.readlines()
