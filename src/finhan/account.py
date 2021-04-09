from dataclasses import dataclass
from datetime import timedelta, datetime
from functools import reduce
from itertools import starmap, chain, groupby
from pathlib import Path
from typing import Dict, Iterator, Collection, Tuple

import yaml

from finhan.account_names import from_file

AccountId = str
Balance = float


@dataclass
class Account:
    id_: AccountId
    balance: Balance
    name: str


def read_balance(
    balance_file: Path, account_names: Dict[AccountId, str]
) -> Dict[AccountId, Account]:
    with balance_file.open() as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    assert config["schema"] == "v1"
    accounts_data = config["accounts"]
    accounts = (
        Account(id_=a["id"], balance=a["balance"], name=account_names[a["id"]])
        for a in accounts_data
    )
    return {a.id_: a for a in accounts}


def read_account_transactions(data_paths, from_lines):
    line_lists = map(read_lines, data_paths)
    transaction_lists = tuple(map(from_lines, line_lists))
    transaction_lists = tuple(
        starmap(lambda ts, account: (tuple(ts), account), transaction_lists)
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


def apply_balance(current_balance, numbers):
    saldo_floating = tuple(cumsum(numbers))
    last_floating_saldo = saldo_floating[-1]
    saldo = array_add(saldo_floating, current_balance - last_floating_saldo)
    return saldo


def cumsum(arr):
    s = 0
    for x in arr:
        s += x
        yield s


def dates_and_numbers(transactions):
    transactions = sorted(transactions, key=lambda t: t.date, reverse=False)
    dates = tuple(t.date for t in transactions)
    numbers = tuple(t.amount for t in transactions)
    return dates, numbers


def joint_account_transactions(
    current_balance, transactions_by_account
) -> Tuple[Collection[datetime], Collection[Balance]]:
    def get_date(transaction):
        return transaction.date

    transactions_by_date = sorted(
        tuple(chain(*transactions_by_account.values())), key=get_date
    )
    total = 0
    joint = []
    for date, transactions in groupby(transactions_by_date, get_date):
        total = total + sum(t.amount for t in transactions)
        joint.append(total)
    joint_current_balance = sum(a.balance for a in current_balance.values())
    return (
        sorted(set(t.date for t in transactions_by_date)),
        array_add(joint, -joint[-1] + joint_current_balance),
    )


def array_add(arr, c):
    return type(arr)(x + c for x in arr)


def read_lines(filename: str) -> Iterator[str]:
    with Path(filename).open() as f:
        return f.readlines()
