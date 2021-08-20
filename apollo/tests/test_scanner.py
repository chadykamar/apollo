import pytest
from exc import UnexpectedCharacter, UnterminatedString
from scanner import Scanner
from tok import Token
from tok import TokenType as tt


def test_scanner_hello_world():
    expected = [
        Token(tt.IDENTIFIER, 1, "print"),
        Token(tt.LPAREN, 1, '('),
        Token(tt.STRING, 1, '"hello, world!"', "hello, world!"),
        Token(tt.RPAREN, 1, ')'),
        Token(tt.EOF, 1)
    ]

    scanner = Scanner('print("hello, world!")')
    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_symbols():

    expected = [
        Token(tt.NEWLINE, 1, '\n'),
        Token(tt.LPAREN, 2, '('),
        Token(tt.LBRACE, 2, '{'),
        Token(tt.LBRACK, 2, '['),
        Token(tt.LESSER, 2, '<'),
        Token(tt.GREATER, 2, '>'),
        Token(tt.RBRACK, 2, ']'),
        Token(tt.RBRACE, 2, '}'),
        Token(tt.RPAREN, 2, ')'),
        Token(tt.NEWLINE, 2, '\n'),
        Token(tt.NEWLINE, 3, '\n'),
        Token(tt.NEWLINE, 4, '\n'),
        Token(tt.NEWLINE, 5, '\n'),
        Token(tt.PLUS, 6, '+'),
        Token(tt.MINUS, 6, '-'),
        Token(tt.STAR, 6, '*'),
        Token(tt.SLASH, 6, '/'),
        Token(tt.PERCENT, 6, '%'),
        Token(tt.DOT, 6, '.'),
        Token(tt.COMMA, 6, ','),
        Token(tt.SCOLON, 6, ';'),
        Token(tt.COLON, 6, ':'),
        Token(tt.NEQUAL, 6, '!='),
        Token(tt.ASSIGN, 6, '='),
        Token(tt.BANG, 6, '!'),
        Token(tt.EQUAL, 6, '=='),
        Token(tt.LEQUAL, 6, '<='),
        Token(tt.GEQUAL, 6, '>='),
        Token(tt.NEWLINE, 6, '\n'),
        Token(tt.EOF, 7)
    ]

    scanner = Scanner("\n({[<>]})\n\n\n\n+-*/%.,;:!==! ==<=>=\n")

    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_keywords():

    expected = [
        Token(tt.IF, 1, 'if'),
        Token(tt.ELIF, 1, 'elif'),
        Token(tt.ELSE, 1, 'else'),
        Token(tt.TRUE, 1, 'True'),
        Token(tt.FALSE, 1, 'False'),
        Token(tt.NONE, 1, 'None'),
        Token(tt.OR, 1, 'or'),
        Token(tt.AND, 1, 'and'),
        Token(tt.NOT, 1, 'not'),
        Token(tt.CLASS, 1, 'class'),
        Token(tt.SELF, 1, 'self'),
        Token(tt.RETURN, 1, 'return'),
        Token(tt.DEF, 1, 'def'),
        Token(tt.IMPORT, 1, 'import'),
        Token(tt.FOR, 1, 'for'),
        Token(tt.WHILE, 1, 'while'),
        Token(tt.DO, 1, 'do'),
        Token(tt.EOF, 1)
    ]

    scanner = Scanner(
        "if elif else True False None or and not class self return def import for while do"
    )

    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_unexpected_char():

    with pytest.raises(UnexpectedCharacter):

        scanner = Scanner("underscore is unexpected _")
        scanner.scan_tokens()


def test_identifier():

    expected = [Token(tt.IDENTIFIER, 1, 'a'), Token(tt.EOF, 1)]

    scanner = Scanner("a")
    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_comment():

    expected = [Token(tt.EOF, 1)]

    scanner = Scanner("""# hello, world!""")

    tokens = scanner.scan_tokens()

    assert tokens == expected


@pytest.mark.parametrize('string', ["'hello'", '"hello"'])
def test_string(string):

    expected = [Token(tt.STRING, 1, string, string[1:-1]), Token(tt.EOF, 1)]

    scanner = Scanner(string)
    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_unterminated_string():

    with pytest.raises(UnterminatedString):

        scanner = Scanner("'hello")
        scanner.scan_tokens()


@pytest.mark.parametrize('num', ["255", '1.5'])
def test_number(num):

    expected = [
        Token(tt.NUMBER, 1, num,
              float(num) if '.' in num else int(num)),
        Token(tt.EOF, 1)
    ]

    scanner = Scanner(num)
    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_assignment():

    expected = [
        Token(tt.IDENTIFIER, 1, 'hello'),
        Token(tt.ASSIGN, 1, '='),
        Token(tt.NUMBER, 1, '1234', 1234),
        Token(tt.EOF, 1)
    ]

    scanner = Scanner("hello = 1234")
    tokens = scanner.scan_tokens()

    assert tokens == expected


def test_indent():

    expected = [
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ':'),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.IDENTIFIER, 3, "print"),
        Token(tt.LPAREN, 3, "("),
        Token(tt.STRING, 3, '"hello"', "hello"),
        Token(tt.RPAREN, 3, ")"),
        Token(tt.DEDENT, 3),
        Token(tt.EOF, 3)
    ]

    text = \
"""
if True:
    print("hello")"""

    scanner = Scanner(text)

    assert scanner.scan_tokens() == expected


def test_dedent():

    expected = [
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.FOR, 2, "for"),
        Token(tt.IDENTIFIER, 2, "i"),
        Token(tt.IN, 2, "in"),
        Token(tt.IDENTIFIER, 2, "range"),
        Token(tt.LPAREN, 2, "("),
        Token(tt.NUMBER, 2, "10", 10),
        Token(tt.RPAREN, 2, ")"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.IF, 3, "if"),
        Token(tt.TRUE, 3, "True"),
        Token(tt.COLON, 3, ':'),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.INDENT, 4, "        "),
        Token(tt.IDENTIFIER, 4, "print"),
        Token(tt.LPAREN, 4, "("),
        Token(tt.STRING, 4, '"hello"', "hello"),
        Token(tt.RPAREN, 4, ")"),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 5),
        Token(tt.DEDENT, 5),
        Token(tt.NUMBER, 5, "1", 1),
        Token(tt.PLUS, 5, "+"),
        Token(tt.NUMBER, 5, "1", 1),
        Token(tt.NEWLINE, 5, "\n"),
        Token(tt.EOF, 6)
    ]

    text = \
"""
for i in range(10):
    if True:
        print("hello")
1 + 1
"""

    scanner = Scanner(text)

    assert scanner.scan_tokens() == expected