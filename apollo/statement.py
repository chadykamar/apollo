

import abc
from dataclasses import dataclass

from expression import Expression


class Statement(abc.ABC):
    pass


@dataclass
class ExpressionStatement(Statement):
    expr: Expression
