from exc import ParseException
from expression import (
    Binary,
    Call,
    CommaExpression,
    Expression,
    Grouping,
    Literal,
    Logical,
    Ternary,
    Unary,
    Variable,
)
from statement import (
    AssignmentStatement,
    Block,
    ExpressionStatement,
    FunctionDefinition,
    IfStmt,
    Statement,
    WhileStmt,
    ReturnStmt,
)
from tok import TokenType as tt
from tok.tok import Token
from tok.type import TokenType


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Statement]:
        statements = []

        while not self.end:
            try:
                statements.append(self.statement())
            except ParseException:
                statements.append(None)
                self.sync()
                raise

        return statements

    def statement(self):

        if self.check(tt.IDENTIFIER) and self.check(tt.ASSIGN, lookahead=True):
            return self.assignment()
        elif self.match(tt.IF):
            return self.if_stmt()
        elif self.match(tt.WHILE):
            return self.while_stmt()
        elif self.match(tt.DEF):
            return self.function()
        elif self.match(tt.RETURN):
            return self.return_stmt()

        return self.expr_stmt()

    def return_stmt(self):
        keyword = self.previous

        if self.match(tt.NEWLINE):
            return ReturnStmt(keyword, None)

        value = self.expression()
        self.consume(tt.NEWLINE, "Expect newline after return")

        return ReturnStmt(keyword, value)

    def function(self):
        name = self.consume(tt.IDENTIFIER, "Expect function name")
        self.consume(tt.LPAREN, "Expect '(' after function name")

        params = []
        if not self.check(tt.RPAREN):
            while True:
                param = Variable(self.consume(tt.IDENTIFIER, "Expect parameter name"))
                params.append(param)

                if not self.match(tt.COMMA):
                    break

        self.consume(tt.RPAREN, "Expect ')' after parameters")
        self.consume(tt.COLON, "Expect ':' after function signature")

        block = self.block()

        return FunctionDefinition(name, params, block)

    def while_stmt(self):
        condition = self.disjunction()

        self.consume(tt.COLON, "expect ':' after while condition")

        block = self.block()

        else_block = None
        if self.match(tt.ELSE):
            else_block = self.else_block()

        return WhileStmt(condition, block, else_block)

    def assignment(self):
        name = self.consume(tt.IDENTIFIER, "expect var name")

        if self.match(tt.ASSIGN):
            expr = self.expression()

        if not self.end:
            self.consume(tt.NEWLINE, "Expect newline after assignment")
        return AssignmentStatement(name, expr)

    def if_stmt(self):
        condition = self.disjunction()

        self.consume(tt.COLON, "expected ':' after if condition")

        block = self.block()

        if self.match(tt.ELIF):
            elif_stmt = self.if_stmt()
            return IfStmt(condition, block, elif_stmt=elif_stmt)
        elif self.match(tt.ELSE):

            else_block = self.else_block()
            return IfStmt(condition, block, else_block=else_block)
        else:
            return IfStmt(condition, block)

    def else_block(self):
        self.consume(tt.COLON, "expected ':' after if condition")
        return self.block()

    def block(self):
        self.consume(tt.NEWLINE, "Expect newline to start block")
        self.consume(tt.INDENT, "Expected block to be indented")

        statements = []
        while not self.match(tt.DEDENT):
            statements.append(self.statement())

        return Block(statements)

    def expr_stmt(self):
        expr = self.disjunction()
        if not self.end:
            self.consume(tt.NEWLINE, "Syntax error")
        return ExpressionStatement(expr)

    def disjunction(self):
        expr = self.conjunction()

        while self.match(tt.OR):
            operator = self.previous
            right = self.conjunction()
            expr = Logical(expr, operator, right)

        return expr

    def conjunction(self):
        expr = self.expression()

        while self.match(tt.AND):
            operator = self.previous
            right = self.expression()
            expr = Logical(expr, operator, right)

        return expr

    def expression(self) -> Expression:
        expr = self.ternary()

        exprs = []
        while self.match(tt.COMMA):
            exprs.append(self.ternary())

        if exprs:
            exprs.insert(0, expr)
            return CommaExpression(exprs)
        else:
            return expr

    def ternary(self) -> Expression:
        expr = self.equality()

        if self.match(tt.IF):
            if_ = self.previous
            condition = self.equality()

            if self.match(tt.ELSE):
                else_ = self.previous
                right = self.equality()
                expr = Ternary(expr, if_, condition, else_, right)

        return expr

    def left_assoc(self, higher_precedence, *types):
        expr = higher_precedence()

        while self.match(*types):
            operator = self.previous
            right = higher_precedence()

            expr = Binary(expr, operator, right)

        return expr

    def equality(self) -> Expression:
        return self.left_assoc(self.comparison, tt.NEQUAL, tt.EQUAL)

    def comparison(self):
        return self.left_assoc(self.term, tt.GREATER, tt.GEQUAL, tt.LESSER, tt.LEQUAL)

    def term(self) -> Expression:
        return self.left_assoc(self.factor, tt.MINUS, tt.PLUS)

    def factor(self) -> Expression:
        return self.left_assoc(self.unary, tt.SLASH, tt.STAR)

    def unary(self):

        if self.match(tt.BANG, tt.MINUS):
            operator = self.previous
            right = self.unary()

            return Unary(operator, right)

        return self.call()

    def call(self) -> Expression:
        expr = self.primary()

        while self.match(tt.LPAREN):
            args = self.expression() if not self.check(tt.RPAREN) else None

            paren = self.consume(tt.RPAREN, "Expect ')' after arguments.")

            return Call(expr, paren, args)

        return expr

    def primary(self):
        if self.match(tt.FALSE):
            return Literal(False)
        elif self.match(tt.TRUE):
            return Literal(True)
        elif self.match(tt.NONE):
            return Literal(None)
        elif self.match(tt.NUMBER, tt.STRING):
            return Literal(self.previous.literal)
        elif self.match(tt.LPAREN):
            expr = self.expression()
            self.consume(tt.RPAREN, "Expect ')' after expression.")
            return Grouping(expr)
        elif self.match(tt.IDENTIFIER):
            return Variable(self.previous)

        raise ParseException("Expression expected.", self.peek())

    def match(self, *types) -> bool:
        """
        Returns True if the current token has any of the given types.
        """
        if self.peek().type in types:
            self.advance()
            return True

        return False

    def sync(self):
        self.advance()

        while not self.end:
            if self.previous.type == tt.NEWLINE:
                return

            if self.match(tt.CLASS, tt.DEF, tt.FOR, tt.IF, tt.WHILE, tt.RETURN):
                return

            self.advance()

    def consume(self, type: TokenType, msg: str):
        if self.check(type):
            return self.advance()

        raise ParseException(msg, self.peek())

    def check(self, type, lookahead=False):
        if self.end:
            return False

        if lookahead:
            return self.lookahead().type == type
        return self.peek().type == type

    def advance(self):
        if not self.end:
            self.current += 1
        return self.previous

    @property
    def end(self):
        return self.peek().type == tt.EOF or (
            self.peek().type == tt.DEDENT and self.lookahead().type == tt.EOF
        )

    def peek(self):
        return self.tokens[self.current]

    def lookahead(self):
        return self.tokens[self.current + 1]

    @property
    def previous(self):
        return self.tokens[self.current - 1]
