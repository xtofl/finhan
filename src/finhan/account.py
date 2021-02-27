from pathlib import Path
from typing import Dict
import yaml

AccountId = str
Balance = float


def read_balance(filename: Path) -> Dict[AccountId, Balance]:
    with filename.open() as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    return {AccountId(a): Balance(b) for a, b in config.items()}

