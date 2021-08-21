from exc import UnexpectedCharacter, UnterminatedString
from tok import Token
from tok import TokenType as tt

EOL = '\n'

KEYWORDS = {
    "and": tt.AND,
    "or": tt.OR,
    "not": tt.NOT,
    "if": tt.IF,
    "elif": tt.ELIF,
    "else": tt.ELSE,
    "True": tt.TRUE,
    "False": tt.FALSE,
    "None": tt.NONE,
    "in": tt.IN,

    "do": tt.DO,
    "for": tt.FOR,
    "while": tt.WHILE,

    "return": tt.RETURN,
    "class": tt.CLASS,
    "def": tt.DEF,
    "self": tt.SELF,
    "import": tt.IMPORT,
}


class Scanner:
    def __init__(self, code: str) -> None:
        self.code = code
        self.tokens : list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.leading_spaces = 0
        self.indents = [0]

    def scan_token(self):

        c = self.advance()
        match c:
            case '(': self.add_token(tt.LPAREN)
            case ')': self.add_token(tt.RPAREN)
            case '{': self.add_token(tt.LBRACE)
            case '}': self.add_token(tt.RBRACE)
            case '[': self.add_token(tt.LBRACK)
            case ']': self.add_token(tt.RBRACK)
            # TODO distinguish lesser from subclass context
            case ',': self.add_token(tt.COMMA)
            case '.': self.add_token(tt.DOT)
            case '+': self.add_token(tt.PLUS)
            case '-': self.add_token(tt.MINUS)
            case '*': self.add_token(tt.STAR)
            case '/': self.add_token(tt.SLASH)
            case '%': self.add_token(tt.PERCENT)
            case ';': self.add_token(tt.SCOLON)
            case ':': self.add_token(tt.COLON)
            case '!': self.add_token(tt.NEQUAL if self.match("=") else tt.BANG)
            case '=': self.add_token(tt.EQUAL if self.match("=") else tt.ASSIGN)
            case '<': self.add_token(tt.LEQUAL if self.match("=") else tt.LESSER)
            case '>': self.add_token(tt.GEQUAL if self.match("=") else tt.GREATER)
            case '#':
                while self.peek():
                    self.advance()
            case ' ':
                if not self.tokens or self.previous.type == tt.NEWLINE:
                    self.leading_spaces += 1
            case '\r' | '\t' : ...
            case '\n':
                self.add_token(tt.NEWLINE)
                self.line += 1
                self.leading_spaces = 0
            case '"' | "'" as quote: self.add_token(tt.STRING, self.string(quote))
            case c if c.isdecimal(): self.add_token(tt.NUMBER, self.number())
            case c if c.isalpha(): self.add_token(self.keyword_identifier())
            case _: raise UnexpectedCharacter(f"Unexpected character {c} at line {self.line}.")

    def match(self, expected):
        """Returns True if the next char is equal to expected"""
        if self.peek() == expected:
            self.current += 1
            return True

        return False

    def string(self, quote):
        start_line = self.line
        while (char := self.peek()) and char != quote:
            if char == EOL:
                self.line += 1
            self.advance()

        if self.end:
            raise UnterminatedString(
                f"String started on line {start_line} is unterminated on line {self.line}.")

        self.advance()

        val = self.code[self.start+1: self.current-1]  # we trim the quotes
        return val

    def number(self):
        is_float = False
        while (c := self.peek()) and c.isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            is_float = True
            self.advance()

            while (c := self.peek()) and c.isdigit():
                self.advance()

        val: str = self.code[self.start: self.current]

        return float(val) if is_float else int(val)

    def keyword_identifier(self):
        while (c := self.peek()) and (c.isalnum() or c == "_"):
            self.advance()

        text = self.code[self.start:self.current]
        type = KEYWORDS.get(text, tt.IDENTIFIER)

        return type

    def peek(self) -> None | str:
        return None if self.end else self.code[self.current]

    @property
    def previous(self):
        if self.tokens:
            return self.tokens[-1]

    def peek_next(self) -> None | str:
        idx = self.current + 1
        return None if idx >= len(self.code) else self.code[idx]

    def advance(self):
        c = self.code[self.current]
        self.current += 1
        return c

    def add_token(self, type, literal=None):
        text = self.code[self.start: self.current]

        # Figure out the indentation
        if self.previous and self.previous.type == tt.NEWLINE:
            self.resolve_indentation_level()

        self.tokens.append(Token(type, self.line, text, literal))


    def resolve_indentation_level(self):

        if self.indents[-1] == self.leading_spaces:
            return
        elif self.indents[-1] < self.leading_spaces:
            self.tokens.append(Token(tt.INDENT, self.line, " "*self.leading_spaces))
            self.indents.append(self.leading_spaces)
            return

        while self.indents[-1] > self.leading_spaces:
            self.indents.pop()
            self.tokens.append(Token(tt.DEDENT, self.line))

        if self.indents[-1] != self.leading_spaces:
            raise IndentationError


        self.leading_spaces = 0

    def scan_tokens(self):
        while not self.end:
            self.start = self.current
            self.scan_token()

        for indent in self.indents:
            if indent > 0:
                self.tokens.append(Token(tt.DEDENT, self.line))

        self.tokens.append(Token(tt.EOF, self.line))
        return self.tokens

    @property
    def end(self):
        return self.current >= len(self.code)
