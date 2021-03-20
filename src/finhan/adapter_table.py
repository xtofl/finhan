import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

from finhan.account import read_account_transactions
from finhan.transaction import Transaction


def _to_row(transaction: Transaction) -> str:
    return (
        f"{transaction.date.strftime('%Y/%m/%d')} "
        f"{transaction.amount:10.2f}"
        f" {transaction.target} "
        f'"{transaction.message}"'
    )


def generate_from(title: str, transactions: Iterable[Transaction]):
    return title + "\n" + "\n".join(map(_to_row, transactions))


class AccountNotFound(Exception):
    def __init__(self, accounts):
        self.accounts = accounts
        super().__init__()


def generate_from_files(account_id: str, files: Iterable[Path]):
    title = "account: " + account_id
    transactions_per_account = read_account_transactions(files)
    try:
        transactions = transactions_per_account[account_id]
    except KeyError:
        raise AccountNotFound(transactions_per_account.keys())
    return generate_from(title, transactions)


def main():
    parser = ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("files", nargs="*")
    options = parser.parse_args()
    try:
        print(generate_from_files(options.account, map(Path, options.files)))
    except AccountNotFound as a:
        print(f"account not found; valid accounts: [{a.accounts}]")


if __name__ == "__main__":
    main()
