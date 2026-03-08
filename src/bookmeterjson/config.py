from dataclasses import dataclass, field
from pathlib import Path

import yaml

VALID_CATEGORIES = {"read", "reading", "stacked", "wish"}


@dataclass
class Config:
    user_id: str
    email: str
    password: str
    categories: list[str] = field(
        default_factory=lambda: ["read", "reading", "stacked", "wish"]
    )
    output_dir: str = "./output"

    def __post_init__(self):
        for cat in self.categories:
            if cat not in VALID_CATEGORIES:
                raise ValueError(
                    f"Invalid category: {cat!r}. Must be one of {VALID_CATEGORIES}"
                )


def load_config(path: str | Path = "configs.yaml") -> Config:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            "Copy configs.example.yaml to configs.yaml and fill in your credentials."
        )
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)
