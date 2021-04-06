#!/usr/bin/env python3
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence, Dict, Iterable

from matplotlib import pyplot
from matplotlib.lines import Line2D

from finhan.account import (
    read_balance,
    read_account_transactions,
    apply_balance,
    dates_and_numbers,
    joint_account_transactions,
    AccountId,
)

import finhan.adapter_bepost.csv_transactions
from finhan.account_names import from_file


@dataclass
class Plot:
    dates: Sequence[datetime]
    balance: Sequence[float]


@dataclass
class Plots:
    grand_total: Plot
    account_plots: Dict[AccountId, Plot]


def plot_grand_total(current_balance, transactions_by_account) -> Plot:
    dates, grand_total = joint_account_transactions(
        current_balance, transactions_by_account
    )
    pyplot.plot_date(dates, grand_total, "-", label=f"GRAND TOTAL", linewidth=4)
    return Plot(dates=dates, balance=grand_total)


def main():
    parser = ArgumentParser()
    parser.add_argument("data_paths", type=str, nargs="*")
    parser.add_argument(
        "--balance",
        type=Path,
        default="balance.yaml",
        help="Path to current balance file.  This file should contain a "
        "dict of account -> balance",
    )
    parser.add_argument(
        "--account-names-file",
        type=str,
        default="account-names.yaml",
        help="yaml file with account names",
    )
    parser.add_argument(
        "--show_transactions",
        action="store_true",
        help="plot each transaction, too",
    )

    options = parser.parse_args()
    account_names = (from_file(Path(options.account_names_file)),)
    create_plots(
        current_balance=read_balance(
            balance_file=Path(options.balance),
            names_file=Path(options.account_names_file),
        ),
        transactions_by_account=read_account_transactions(
            data_paths=options.data_paths,
            from_lines=finhan.adapter_bepost.csv_transactions.from_lines,
        ),
        show_transactions=options.show_transactions,
    )
    pyplot.show()


def create_plots(
    current_balance, transactions_by_account, show_transactions
) -> Plots:
    print(current_balance)
    account_plots = tuple(
        plot_each_account(
            current_balance,
            transactions_by_account,
            show_transactions=show_transactions,
        )
    )
    grand = plot_grand_total(current_balance, transactions_by_account)
    pyplot.grid()
    pyplot.legend()
    return Plots(grand_total=grand, account_plots=account_plots)


def plot_each_account(
    current_balance, transactions_by_account, show_transactions: bool
) -> Iterable[Plot]:
    for account_id, transactions in transactions_by_account.items():
        yield plot_for_account(
            current_balance.get(account_id, None),
            transactions,
            show_transactions,
        )


def plot_for_account(account, transactions, show_transactions) -> Plot:
    dates, numbers = dates_and_numbers(transactions)

    balance = apply_balance(account.balance, numbers)
    print(f"plotting for account {account}")
    line: Line2D = pyplot.plot_date(
        dates,
        balance,
        "-",
        linewidth=0.4,
        label=f"balance {account.id_} ({account.name})",
    )[0]
    if show_transactions:
        pyplot.plot_date(
            dates, numbers, "+", label=account.id_, color=line.get_color()
        )
    return Plot(dates=dates, balance=balance)


if __name__ == "__main__":
    main()
