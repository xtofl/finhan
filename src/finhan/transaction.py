from dataclasses import dataclass, astuple
from datetime import datetime
from typing import Union, Tuple


@dataclass
class Transaction:
    date: datetime
    source: str
    target: str
    amount: float
    message: Union[str, Tuple[int]] = "-no message-"

    def __hash__(self):
        return hash(astuple(self))
