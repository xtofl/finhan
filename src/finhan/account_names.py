from pathlib import Path

import yaml


def from_file(file: Path):
    if not file.exists():
        return {}

    with file.open() as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        assert data["schema"] == "v1", "Only support this version, yet"
        accounts = data["accounts"]
        return {a["id"]: a["name"] for a in accounts}
