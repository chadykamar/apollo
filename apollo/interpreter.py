
from token import NUMBER

from exc import RuntimeException
from expression import Binary, Expression, Grouping, Literal, Ternary, Unary
from statement import ExpressionStatement, Statement
from tok.type import TokenType as tt


class Interpreter:

    def interpret(self, statements: list[Statement]):
        results = []
        for stmt in statements:
            results.append(self.execute(stmt))
        return results

    def execute(self, statement: Statement):

        match statement:
            case ExpressionStatement() as stmt: return self.evaluate(stmt.expr)

    def evaluate(self, expr: Expression):

        match expr:
            case Unary() as expr: return self.unary(expr)
            case Binary() as expr: return self.binary(expr)
            case Literal() as expr: return self.literal(expr)
            case Grouping() as expr: return self.grouping(expr)
            case Ternary() as expr: return self.ternary(expr)

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
