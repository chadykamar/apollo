from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any

from tok import Token


class Expression(abc.ABC):
    pass


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class Literal(Expression):
    value: Any
