

import abc
from dataclasses import dataclass

from expression import Expression
from tok import Token


class Statement(abc.ABC):
    pass


@dataclass
class ExpressionStatement(Statement):
    expr: Expression


@dataclass
class AssignmentStatement(Statement):
    name: Token
    expr: Expression
