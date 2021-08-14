from dataclasses import dataclass
from typing import Any, Optional

from .type import TokenType


@dataclass
class Token:
    type: TokenType
    line: int
    lexeme: Optional[str] = None
    literal: Optional[Any] = None
