from datetime import datetime
from pathlib import Path

import pytest

from finhan.account import (
    apply_balance,
    joint_account_transactions,
    Account,
    read_balance,
)
from finhan.adapter_bepost.csv_transactions import Transaction
from finhan.main import create_plots, Plots

A = "BE123456789"
B = "BE987654321"
C = "external"

d1 = datetime(year=2021, month=2, day=1)
d2 = datetime(year=2021, month=2, day=2)
d3 = datetime(year=2021, month=5, day=3)

transactions_a = (
    # start with 1000
    Transaction(d1, A, B, 100),
    Transaction(d2, A, C, 100),
)

transactions_b = (
    # start with 2000
    Transaction(d1, B, A, -100),
    Transaction(d3, B, A, -100),
)


def test_all_accounts_are_plotted(tmp_path):
    plots: Plots = create_plots(
        transactions_by_account={"A": transactions_a, "B": transactions_b},
        show_transactions=True,
        current_balance={
            "A": Account(id_="A", balance=1200, name="a"),
            "B": Account(id_="B", balance=1800, name="b"),
        },
    )
    assert plots.grand_total is not None
    assert tuple(plots.grand_total.dates) == (d1, d2, d3)
    assert tuple(plots.grand_total.balance) == (3000, 3100, 3000)
    assert len(plots.account_plots) == 2

    plot1, plot2 = plots.account_plots

    assert tuple(plot1.dates) == (d1, d2)
    assert tuple(plot1.balance) == (1100, 1200)

    assert tuple(plot2.dates) == (d1, d3)
    assert tuple(plot2.balance) == (1900, 1800)
