from datetime import datetime

from finhan.account import apply_balance, joint_account_transactions
from finhan.adapters.bepost import Transaction


def test_balance_series_ends_in_current_balance():
    numbers = (1, 2, 3, 4)
    balance = tuple(apply_balance(100, numbers))
    assert balance[-1] == 100
    assert balance == (91, 93, 96, 100)


def test_grand_total_ends_in_grand_balance():
    d1 = datetime(year=2021, month=2, day=1)
    d2 = datetime(year=2021, month=2, day=2)
    d3 = datetime(year=2021, month=5, day=3)

    transactions = {
        'A': (
            Transaction(source='A', target='X', amount=100, date=d1),
            Transaction(source='A', target='B', amount=10, date=d1),
            Transaction(source='A', target='B', amount=-10, date=d2),
            Transaction(source='A', target='Y', amount=-50, date=d3),
        ),
        'B': (
            Transaction(source='B', target='A', amount=-10, date=d1),
            Transaction(source='B', target='A', amount=10, date=d2),
        )
    }
    balances = {'A': 1010, 'B': -10}

    dates, numbers = joint_account_transactions(balances, transactions)
    assert tuple(dates) == (d1, d2, d3)
    assert numbers[-1] == 1000
    assert tuple(numbers) == (1050, 1050, 1000)
