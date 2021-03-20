from typing import Iterable

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
