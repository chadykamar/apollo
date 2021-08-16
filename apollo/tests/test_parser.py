from parser import Parser

import pytest
from exc import ParseException
from expression import Binary, Grouping, Literal, Ternary, Unary, Variable
from tok import Token
from tok import TokenType as tt
from statement import AssignmentStatement, ExpressionStatement


def test_ternary_if_else():
    # Token = Mock(spec=tok.Token)
    # tt = Mock(spec=tok.TokenType)

    tokens = [Token(tt.NUMBER, 1, '1', 1),
              Token(tt.IF, 1, 'if'),
              Token(tt.TRUE, 1, 'True', True),
              Token(tt.ELSE, 1, 'else'),
              Token(tt.NUMBER, 1, '2', 2),
              Token(tt.EOF, 1)
              ]

    expected = [ExpressionStatement(expr=Ternary(left=Literal(value=1),
                                                 if_=Token(type=tt.IF, line=1,
                                                           lexeme='if', literal=None),
                                                 condition=Literal(value=True),
                                                 else_=Token(type=tt.ELSE,
                                                             line=1,
                                                             lexeme='else',
                                                             literal=None),
                                                 right=Literal(value=2)))]

    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comma_expression():
    tokens = [Token(tt.NUMBER, 1, '1', 1),
              Token(tt.COMMA, 1, ','),
              Token(tt.TRUE, 1, 'True', True),
              Token(tt.COMMA, 1, ','),
              Token(tt.NUMBER, 1, '3', 3),
              Token(tt.EOF, 1)
              ]
    expected = [ExpressionStatement(Binary(Binary(Literal(1), Token(tt.COMMA, 1, ','), Literal(True)),
                                           Token(tt.COMMA, 1, ','),
                                           Literal(3)))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_unary():
    tokens = [Token(tt.MINUS, 1, '-'),
              Token(tt.NUMBER, 1, '1', 1),
              Token(tt.EOF, 1)
              ]
    expected = [ExpressionStatement(
        Unary(Token(tt.MINUS, line=1, lexeme='-'), Literal(1)))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comparison():
    tokens = [Token(tt.TRUE, 1, 'True', True),
              Token(tt.EQUAL, 1, '=='),
              Token(tt.FALSE, 1, 'False', False),
              Token(tt.EOF, 1)
              ]
    expected = [ExpressionStatement(Binary(Literal(True), Token(
        tt.EQUAL, line=1, lexeme='=='), Literal(False)))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_correct():
    tokens = [Token(tt.LPAREN, 1, '('),
              Token(tt.STRING, 1, '"hello"', "hello"),
              Token(tt.RPAREN, 1, ')'),
              Token(tt.EOF, 1)
              ]
    expected = [ExpressionStatement(Grouping(Literal("hello")))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_missing_closing():
    tokens = [Token(tt.LPAREN, 1, '('),
              Token(tt.STRING, 1, '"hello"', "hello"),
              Token(tt.EOF, 1)
              ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_incomplete():
    tokens = [Token(tt.NUMBER, 1, '1', 1),
              Token(tt.PLUS, 1, '+'),
              Token(tt.EOF, 1)
              ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_invalid():
    tokens = [Token(tt.NUMBER, 1, '1', 1),
              Token(tt.PLUS, 1, '+'),
              Token(tt.PLUS, 1, '+'),
              Token(tt.NUMBER, 1, '+'),
              Token(tt.NEWLINE, 1, '\n'),
              Token(tt.EOF, 1)
              ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_expr_statement():
    tokens = [Token(tt.NUMBER, 1, '1', 1),
              Token(tt.PLUS, 1, '+'),
              Token(tt.NUMBER, 1, '1', 1),
              Token(tt.NEWLINE, 1, '\n'),

              Token(tt.NUMBER, 2, '2', 2),
              Token(tt.EOF, 2)]

    parser = Parser(tokens)

    expected = [ExpressionStatement(
        Binary(Literal(1), Token(tt.PLUS, 1, '+'), Literal(1))),

        ExpressionStatement(Literal(2))]

    assert parser.parse() == expected


def test_assignment():
    tokens = [Token(tt.IDENTIFIER, 1, 'a'),
              Token(tt.ASSIGN, 1, '='),
              Token(tt.NUMBER, 1, '1', 1),
              Token(tt.NEWLINE, 1, '\n'),
              Token(tt.EOF, 2)]

    parser = Parser(tokens)

    expected = [AssignmentStatement(name=Token(
        tt.IDENTIFIER, 1, 'a'), expr=Literal(1))]

    assert parser.parse() == expected


def test_none():
    tokens = [Token(tt.NONE, 1, 'None'),
              Token(tt.NEWLINE, 1, '\n'),

              Token(tt.EOF, 2)]

    parser = Parser(tokens)

    expected = [ExpressionStatement(expr=Literal(None))]

    assert parser.parse() == expected


def test_identifier():
    tokens = [Token(tt.IDENTIFIER, 1, 'a'),
              Token(tt.NEWLINE, 1, '\n'),

              Token(tt.EOF, 2)]

    parser = Parser(tokens)

    expected = [ExpressionStatement(
        expr=Variable(Token(tt.IDENTIFIER, 1, 'a')))]

    assert parser.parse() == expected
