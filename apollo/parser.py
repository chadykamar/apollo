
import pysnooper

from exc import ParseException
from expression import Binary, Expression, Grouping, Literal, Ternary, Unary
from tok import TokenType as tt
from tok.tok import Token
from tok.type import TokenType


class Parser:

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Expression | None:
        try:
            return self.expression()
        except ParseException as e:
            raise e

    def expression(self) -> Expression:
        return self.left_assoc(self.ternary, tt.COMMA)

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

        return self.primary()

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
            if self.previous.type == tt.SCOLON:
                return

            if self.match(tt.CLASS, tt.DEF, tt.FOR, tt.IF, tt.WHILE, tt.RETURN):
                return

            self.advance()

    def consume(self, type: TokenType, msg: str):
        if self.check(type):
            return self.advance()

        raise ParseException(msg, self.peek())

    def check(self, type):
        if self.end:
            return False

        return self.peek().type == type

    def advance(self):
        if not self.end:
            self.current += 1
        return self.previous

    @ property
    def end(self):
        return self.peek().type == tt.EOF

    def peek(self):
        return self.tokens[self.current]

    @property
    def previous(self):
        return self.tokens[self.current - 1]