
from token import NUMBER
from typing import Any

from environment import Environment, global_env
from exc import NameNotFoundException, ReturnException, RuntimeException
from expression import (Binary, Call, CommaExpression, Expression, Grouping,
                        Literal, Logical, Ternary, Unary, Variable)
from statement import (AssignmentStatement, Block, ElifStmt, ElseBlock,
                       ExpressionStatement, FunctionDefinition, IfStmt, ReturnStmt, Statement, WhileStmt)
from tok.type import TokenType as tt


class Interpreter:

    def __init__(self) -> None:
        self.globals = global_env()
        self.env = Environment(enclosing=self.globals)

    def interpret(self, statements: list[Statement]):
        results = []
        for stmt in statements:
            try:
                res = self.execute(stmt)
                if isinstance(res, list):
                    results.extend(res)
                else:
                    results.append(res)
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
                    self.execute(block)
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
            case FunctionDefinition(name, params, block) as func_def:
                function = Function(func_def)
                self.env[func_def.name.lexeme] = function
            case ReturnStmt(keyword, value):

                if value:
                    value = self.evaluate(value)

                raise ReturnException("Return value", keyword, value)


    def evaluate(self, expr: Expression) -> Any:

        match expr:
            case Logical() as expr: return self.logical(expr)
            case Unary() as expr: return self.unary(expr)
            case Binary() as expr: return self.binary(expr)
            case Literal() as expr: return self.literal(expr)
            case Grouping() as expr: return self.grouping(expr)
            case Ternary() as expr: return self.ternary(expr)
            case Variable() as expr: return self.env[expr.name.lexeme]
            case CommaExpression() as expr: return [self.evaluate(e) for e in expr.expressions]
            case Call(callee, _, args):
                try:
                    self.call(callee, args)
                except ReturnException as e:
                    return e.value


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

    def call(self, callee, args: list[Expression] | Expression | None) -> Any:
        from functools import partial

        callee = self.evaluate(callee)

        if isinstance(callee, Function):
            callee = partial(callee, self)

        if isinstance(args, Expression):
            return callee(self.evaluate(args))
        elif args == None:
            return callee()
        elif isinstance(args, CommaExpression):
            args = [self.evaluate(arg) for arg in args.expressions]
            return callee(*args)


class Function:
    def __init__(self, definition: FunctionDefinition):
        self.definition = definition

    def __call__(self, interpreter: Interpreter, *args) -> Any:
        env = Environment(enclosing=interpreter.globals)
        for i, arg in enumerate(args):
            env[self.definition.params[i].name.lexeme] = arg

        interpreter.execute(self.definition.block)
