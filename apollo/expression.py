from __future__ import annotations

import abc
from dataclasses import dataclass, field
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
class Ternary(Expression):
    """Ternary expressions, basically only 'a if x else b'"""

    left: Expression
    if_: Token
    condition: Expression
    else_: Token
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


@dataclass
class Variable(Expression):
    name: Token


@dataclass
class Logical(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    arguments: CommaExpression | None = None


@dataclass
class CommaExpression:
    expressions: list[Expression]
