
from token import NUMBER

from environment import Environment
from exc import NameNotFoundException, RuntimeException
from expression import (Binary, Expression, Grouping, Literal, Logical, Ternary, Unary,
                        Variable)
from statement import AssignmentStatement, Block, ElifStmt, ElseBlock, ExpressionStatement, IfStmt, Statement, WhileStmt
from tok.type import TokenType as tt


class Interpreter:

    def __init__(self) -> None:
        self.env = Environment()

    def interpret(self, statements: list[Statement]):
        results = []
        for stmt in statements:
            try:
                results.append(self.execute(stmt))
            except NameNotFoundException as e:
                results.append(None)
                print(e)
                raise
        return results

    def execute(self, statement: Statement):

        match statement:
            case ExpressionStatement() as stmt: return self.evaluate(stmt.expr)
            case AssignmentStatement(name, expr):
                self.env[name.lexeme] = self.evaluate(expr)
            case IfStmt(condition, block, elif_stmt, else_block):
                if self.evaluate(condition):
                    self.interpret(block.statements)
                elif elif_stmt:
                    self.execute(elif_stmt)
                elif else_block:
                    self.execute(else_block)
            case Block(statements):
                for stmt in statements:
                    self.execute(stmt)
            case WhileStmt(condition, block, else_block):
                while self.evaluate(condition):
                    self.execute(block)
                else:
                    if else_block:
                        self.execute(else_block)


    def evaluate(self, expr: Expression):

        match expr:
            case Logical() as expr: return self.logical(expr)
            case Unary() as expr: return self.unary(expr)
            case Binary() as expr: return self.binary(expr)
            case Literal() as expr: return self.literal(expr)
            case Grouping() as expr: return self.grouping(expr)
            case Ternary() as expr: return self.ternary(expr)
            case Variable() as expr: return self.env[expr.name.lexeme]

    def literal(self, expr: Literal):
        return expr.value

    def unary(self, expr: Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.MINUS:
                return -right
            case tt.NOT:
                return not bool(right)

    def ternary(self, expr: Ternary):
        return self.evaluate(expr.left) if self.evaluate(expr.condition) else self.evaluate(expr.right)

    def grouping(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        try:
            match expr.operator.type:
                case tt.MINUS: return left - right
                case tt.SLASH: return left / right
                case tt.STAR: return left * right
                case tt.PLUS: return left + right
                case tt.GREATER: return left > right
                case tt.GEQUAL: return left >= right
                case tt.LESSER: return left < right
                case tt.LEQUAL: return left <= right
                case tt.EQUAL: return left == right
                case tt.NEQUAL: return left != right
        except (TypeError, ZeroDivisionError) as e:
            raise RuntimeException(str(e), expr.operator)

    def logical(self, expr: Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == tt.AND:

            if not left: return left

        elif expr.operator.type == tt.OR:

            if left: return left

        return self.evaluate(expr.right)


