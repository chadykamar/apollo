from typing import Any, Optional
from dataclasses import dataclass


from .type import TokenType


@dataclass
class Token:
    type: TokenType
    line: int
    lexeme: Optional[str] = None
    literal: Optional[Any] = None
