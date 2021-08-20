from parser import Parser

import pytest
from exc import ParseException
from expression import Binary, Grouping, Literal, Ternary, Unary, Variable
from statement import (AssignmentStatement, Block, ElifStmt,
                       ExpressionStatement, IfStmt)
from tok import Token
from tok import TokenType as tt


def test_ternary_if_else():
    # Token = Mock(spec=tok.Token)
    # tt = Mock(spec=tok.TokenType)

    tokens = [
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.IF, 1, 'if'),
        Token(tt.TRUE, 1, 'True', True),
        Token(tt.ELSE, 1, 'else'),
        Token(tt.NUMBER, 1, '2', 2),
        Token(tt.EOF, 1)
    ]

    expected = [
        ExpressionStatement(expr=Ternary(
            left=Literal(value=1),
            if_=Token(type=tt.IF, line=1, lexeme='if', literal=None),
            condition=Literal(value=True),
            else_=Token(type=tt.ELSE, line=1, lexeme='else', literal=None),
            right=Literal(value=2)))
    ]

    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comma_expression():
    tokens = [
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.COMMA, 1, ','),
        Token(tt.TRUE, 1, 'True', True),
        Token(tt.COMMA, 1, ','),
        Token(tt.NUMBER, 1, '3', 3),
        Token(tt.EOF, 1)
    ]
    expected = [
        ExpressionStatement(
            Binary(Binary(Literal(1), Token(tt.COMMA, 1, ','), Literal(True)),
                   Token(tt.COMMA, 1, ','), Literal(3)))
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_unary():
    tokens = [
        Token(tt.MINUS, 1, '-'),
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.EOF, 1)
    ]
    expected = [
        ExpressionStatement(
            Unary(Token(tt.MINUS, line=1, lexeme='-'), Literal(1)))
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comparison():
    tokens = [
        Token(tt.TRUE, 1, 'True', True),
        Token(tt.EQUAL, 1, '=='),
        Token(tt.FALSE, 1, 'False', False),
        Token(tt.EOF, 1)
    ]
    expected = [
        ExpressionStatement(
            Binary(Literal(True), Token(tt.EQUAL, line=1, lexeme='=='),
                   Literal(False)))
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_correct():
    tokens = [
        Token(tt.LPAREN, 1, '('),
        Token(tt.STRING, 1, '"hello"', "hello"),
        Token(tt.RPAREN, 1, ')'),
        Token(tt.EOF, 1)
    ]
    expected = [ExpressionStatement(Grouping(Literal("hello")))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_missing_closing():
    tokens = [
        Token(tt.LPAREN, 1, '('),
        Token(tt.STRING, 1, '"hello"', "hello"),
        Token(tt.EOF, 1)
    ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_incomplete():
    tokens = [
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.PLUS, 1, '+'),
        Token(tt.EOF, 1)
    ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_invalid():
    tokens = [
        Token(tt.NUMBER, 1, '1', 1),
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
    tokens = [
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.PLUS, 1, '+'),
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.NEWLINE, 1, '\n'),
        Token(tt.NUMBER, 2, '2', 2),
        Token(tt.EOF, 2)
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(
            Binary(Literal(1), Token(tt.PLUS, 1, '+'), Literal(1))),
        ExpressionStatement(Literal(2))
    ]

    assert parser.parse() == expected


def test_assignment():
    tokens = [
        Token(tt.IDENTIFIER, 1, 'a'),
        Token(tt.ASSIGN, 1, '='),
        Token(tt.NUMBER, 1, '1', 1),
        Token(tt.NEWLINE, 1, '\n'),
        Token(tt.EOF, 2)
    ]

    parser = Parser(tokens)

    expected = [
        AssignmentStatement(name=Token(tt.IDENTIFIER, 1, 'a'), expr=Literal(1))
    ]

    assert parser.parse() == expected


def test_none():
    tokens = [
        Token(tt.NONE, 1, 'None'),
        Token(tt.NEWLINE, 1, '\n'),
        Token(tt.EOF, 2)
    ]

    parser = Parser(tokens)

    expected = [ExpressionStatement(expr=Literal(None))]

    assert parser.parse() == expected


def test_identifier():
    tokens = [
        Token(tt.IDENTIFIER, 1, 'a'),
        Token(tt.NEWLINE, 1, '\n'),
        Token(tt.EOF, 2)
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(expr=Variable(Token(tt.IDENTIFIER, 1, 'a')))
    ]

    assert parser.parse() == expected


def test_simple_if_stmt():
    tokens = [
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ':'),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.EOF, 3)
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(Literal(True), Block([ExpressionStatement(Literal(1))]))
    ]

    assert parser.parse() == expected


def test_if_stmt_multiple_stmt_block():
    tokens = [
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ':'),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.EOF, 4)
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block([
                ExpressionStatement(Literal(1)),
                ExpressionStatement(Literal(1))
            ]))
    ]

    assert parser.parse() == expected


def test_elif():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ':'),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.NUMBER, 2, "1", 1),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.ELIF, 3, "elif"),
        Token(tt.FALSE, 3, "False"),
        Token(tt.COLON, 3, ":"),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.INDENT, 4, "    "),
        Token(tt.NUMBER, 4, "1", 2),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 5),
        Token(tt.EOF, 5),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(Literal(True),
               Block([ExpressionStatement(Literal(1))]),
               elif_stmt=ElifStmt(Literal(False),
                                  Block([ExpressionStatement(Literal(2))])))
    ]

    assert parser.parse() == expected


def test_else():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ':'),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.NUMBER, 2, "1", 1),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.ELSE, 3, "else"),
        Token(tt.COLON, 3, ":"),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.INDENT, 4, "    "),
        Token(tt.NUMBER, 4, "1", 2),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 5),
        Token(tt.EOF, 5),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(Literal(True),
               Block([ExpressionStatement(Literal(1))]),
               else_block=Block([ExpressionStatement(Literal(2))]))
    ]

    assert parser.parse() == expected


def test_nested_if():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ':'),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ':'),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "        "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.DEDENT, 4),
        Token(tt.EOF, 4)
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block([
                IfStmt(
                    Literal(True),
                    Block([
                        ExpressionStatement(Literal(1)),
                        ExpressionStatement(Literal(1))
                    ]))
            ]))
    ]

    assert parser.parse() == expected
