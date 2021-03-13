#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

from matplotlib import pyplot
from matplotlib.lines import Line2D

from finhan.account import read_balance, read_account_transactions, \
    apply_balance, \
    dates_and_numbers, joint_account_transactions


def plot_grand_total(current_balance, transactions_by_account):
    dates, grand_total = joint_account_transactions(current_balance,
                                                    transactions_by_account)
    pyplot.plot_date(dates, grand_total, '-', label=f'GRAND TOTAL',
                     linewidth=4)


def main():
    parser = ArgumentParser()
    parser.add_argument('data_paths', type=str, nargs='*')
    parser.add_argument(
        '--balance', type=Path,
        help='Path to current balance file.  This file should contain a '
             'dict of account -> balance')
    parser.add_argument(
        '--show_transactions', action='store_true',
        help='plot each transaction, too')

    options = parser.parse_args()

    current_balance = read_balance(options.balance)
    print(current_balance)
    transactions_by_account = read_account_transactions(options.data_paths)
    plot_each_account(current_balance, transactions_by_account,
                      show_transactions=options.show_transactions)
    plot_grand_total(current_balance, transactions_by_account)
    pyplot.grid()
    pyplot.legend()
    pyplot.show()


def plot_each_account(current_balance, transactions_by_account,
                      show_transactions: bool):
    for account_id, transactions in transactions_by_account.items():
        plot_for_account(current_balance.get(account_id, None),
                         transactions,
                         show_transactions)


def plot_for_account(account, transactions,
                     show_transactions):
    dates, numbers = dates_and_numbers(transactions)

    balance = apply_balance(account.balance, numbers)
    print(f'plotting for account {account}')
    line: Line2D = pyplot.plot_date(
        dates, balance, '-', linewidth=.4,
        label=f'balance {account.id_} ({account.name})')[0]
    if show_transactions:
        pyplot.plot_date(dates, numbers, '+', label=account.id_,
                         color=line.get_color())


if __name__ == '__main__':
    main()
