from pathlib import Path
from typing import Dict
import yaml

AccountId = str
Balance = float


def read_balance(filename: Path) -> Dict[AccountId, Balance]:
    with filename.open() as f:
        return {AccountId(a): Balance(b) for a, b in yaml.load(f).items()}

