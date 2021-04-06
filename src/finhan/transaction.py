from dataclasses import dataclass, astuple
from datetime import datetime
from typing import Union, Tuple
from .account import AccountId


@dataclass
class Transaction:
    date: datetime
    source: AccountId
    target: AccountId
    amount: float
    message: Union[str, Tuple[int]] = "-no message-"

    def __hash__(self):
        return hash(astuple(self))
