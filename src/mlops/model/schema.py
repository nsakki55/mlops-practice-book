from dataclasses import dataclass
from typing import Any


@dataclass
class Schema:
    name: str
    dtype: str
    null_value: Any
