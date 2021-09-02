from __future__ import annotations

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


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class IfStmt(Statement):
    condition: Expression
    block: Block
    elif_stmt: None | ElifStmt = None
    else_block: None | ElseBlock = None


ElifStmt = IfStmt

ElseBlock = Block


@dataclass
class WhileStmt(Statement):
    condition: Expression
    block: Block
    else_block: None | ElseBlock = None