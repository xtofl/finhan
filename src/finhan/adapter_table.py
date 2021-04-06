from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable, Callable, Dict

from finhan.account import read_account_transactions, AccountId
from finhan.account_names import from_file
from finhan.transaction import Transaction
import finhan.adapter_bepost.csv_transactions


def _to_row(party_names) -> Callable[[Transaction], str]:
    def f(transaction: Transaction) -> str:
        unknown = "?"
        return (
            f"{transaction.date.strftime('%Y/%m/%d')} "
            f"{transaction.amount:10.2f} "
            f"{transaction.target} "
            f'"{party_names.get(transaction.target, unknown)}" '
            f'"{transaction.message}"'
        )

    return f


def generate_from(
    title: str,
    transactions: Iterable[Transaction],
    account_names: Dict[AccountId, str],
):
    return title + "\n" + "\n".join(map(_to_row(account_names), transactions))


class AccountNotFound(Exception):
    def __init__(self, accounts):
        self.accounts = accounts
        super().__init__()


def read_transactions(
    account_id: str,
    from_lines: Callable[[str], Transaction],
    files: Iterable[Path],
):
    transactions_per_account = read_account_transactions(files, from_lines)
    try:
        return transactions_per_account[account_id]
    except KeyError:
        raise AccountNotFound(transactions_per_account.keys())


def main():
    parser = ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("--file-format", default="bepost")
    parser.add_argument(
        "--account-names-file",
        type=str,
        default="account-names.yaml",
        help="yaml file with account names",
    )
    parser.add_argument("files", nargs="*")
    options = parser.parse_args()

    adapters = {"bepost": finhan.adapter_bepost.csv_transactions.from_lines}

    try:
        transactions = read_transactions(
            account_id=options.account,
            from_lines=adapters[options.file_format],
            files=map(Path, options.files),
        )
        print(
            generate_from(
                title="account: " + options.account,
                transactions=transactions,
                account_names=from_file(Path(options.account_names_file)),
            )
        )
    except AccountNotFound as a:
        print(f"account not found; valid accounts: [{a.accounts}]")


if __name__ == "__main__":
    main()
