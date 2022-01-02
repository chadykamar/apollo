from parser import Parser

import pytest
from exc import ParseException
from expression import (
    Binary,
    Call,
    CommaExpression,
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
    ElifStmt,
    ElseBlock,
    ExpressionStatement,
    FunctionDefinition,
    IfStmt,
    WhileStmt,
)
from tok import Token
from tok import TokenType as tt


def test_ternary_if_else():
    # Token = Mock(spec=tok.Token)
    # tt = Mock(spec=tok.TokenType)

    tokens = [
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True", True),
        Token(tt.ELSE, 1, "else"),
        Token(tt.NUMBER, 1, "2", 2),
        Token(tt.EOF, 1),
    ]

    expected = [
        ExpressionStatement(
            expr=Ternary(
                left=Literal(value=1),
                if_=Token(type=tt.IF, line=1, lexeme="if", literal=None),
                condition=Literal(value=True),
                else_=Token(type=tt.ELSE, line=1, lexeme="else", literal=None),
                right=Literal(value=2),
            )
        )
    ]

    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comma_expression():
    tokens = [
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.COMMA, 1, ","),
        Token(tt.TRUE, 1, "True", True),
        Token(tt.COMMA, 1, ","),
        Token(tt.NUMBER, 1, "3", 3),
        Token(tt.EOF, 1),
    ]
    expected = [
        ExpressionStatement(CommaExpression([Literal(1), Literal(True), Literal(3)]))
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_unary():
    tokens = [Token(tt.MINUS, 1, "-"), Token(tt.NUMBER, 1, "1", 1), Token(tt.EOF, 1)]
    expected = [
        ExpressionStatement(Unary(Token(tt.MINUS, line=1, lexeme="-"), Literal(1)))
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_comparison():
    tokens = [
        Token(tt.TRUE, 1, "True", True),
        Token(tt.EQUAL, 1, "=="),
        Token(tt.FALSE, 1, "False", False),
        Token(tt.EOF, 1),
    ]
    expected = [
        ExpressionStatement(
            Binary(Literal(True), Token(tt.EQUAL, line=1, lexeme="=="), Literal(False))
        )
    ]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_correct():
    tokens = [
        Token(tt.LPAREN, 1, "("),
        Token(tt.STRING, 1, '"hello"', "hello"),
        Token(tt.RPAREN, 1, ")"),
        Token(tt.EOF, 1),
    ]
    expected = [ExpressionStatement(Grouping(Literal("hello")))]
    parser = Parser(tokens)
    assert parser.parse() == expected


def test_grouping_missing_closing():
    tokens = [
        Token(tt.LPAREN, 1, "("),
        Token(tt.STRING, 1, '"hello"', "hello"),
        Token(tt.EOF, 1),
    ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_incomplete():
    tokens = [Token(tt.NUMBER, 1, "1", 1), Token(tt.PLUS, 1, "+"), Token(tt.EOF, 1)]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_invalid():
    tokens = [
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.PLUS, 1, "+"),
        Token(tt.PLUS, 1, "+"),
        Token(tt.NUMBER, 1, "+"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.EOF, 1),
    ]
    parser = Parser(tokens)
    with pytest.raises(ParseException):
        parser.parse()


def test_expr_statement():
    tokens = [
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.PLUS, 1, "+"),
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.NUMBER, 2, "2", 2),
        Token(tt.EOF, 2),
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(Binary(Literal(1), Token(tt.PLUS, 1, "+"), Literal(1))),
        ExpressionStatement(Literal(2)),
    ]

    assert parser.parse() == expected


def test_assignment():
    tokens = [
        Token(tt.IDENTIFIER, 1, "a"),
        Token(tt.ASSIGN, 1, "="),
        Token(tt.NUMBER, 1, "1", 1),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.EOF, 2),
    ]

    parser = Parser(tokens)

    expected = [AssignmentStatement(name=Token(tt.IDENTIFIER, 1, "a"), expr=Literal(1))]

    assert parser.parse() == expected


def test_none():
    tokens = [Token(tt.NONE, 1, "None"), Token(tt.NEWLINE, 1, "\n"), Token(tt.EOF, 2)]

    parser = Parser(tokens)

    expected = [ExpressionStatement(expr=Literal(None))]

    assert parser.parse() == expected


def test_identifier():
    tokens = [
        Token(tt.IDENTIFIER, 1, "a"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.EOF, 2),
    ]

    parser = Parser(tokens)

    expected = [ExpressionStatement(expr=Variable(Token(tt.IDENTIFIER, 1, "a")))]

    assert parser.parse() == expected


def test_simple_if_stmt():
    tokens = [
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.EOF, 3),
    ]

    parser = Parser(tokens)

    expected = [IfStmt(Literal(True), Block([ExpressionStatement(Literal(1))]))]

    assert parser.parse() == expected


def test_if_stmt_multiple_stmt_block():
    tokens = [
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "    "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.EOF, 4),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block([ExpressionStatement(Literal(1)), ExpressionStatement(Literal(1))]),
        )
    ]

    assert parser.parse() == expected


def test_elif():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
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
        IfStmt(
            Literal(True),
            Block([ExpressionStatement(Literal(1))]),
            elif_stmt=ElifStmt(
                Literal(False), Block([ExpressionStatement(Literal(2))])
            ),
        )
    ]

    assert parser.parse() == expected


def test_else():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
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
        IfStmt(
            Literal(True),
            Block([ExpressionStatement(Literal(1))]),
            else_block=Block([ExpressionStatement(Literal(2))]),
        )
    ]

    assert parser.parse() == expected


def test_nested_if():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "        "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.DEDENT, 4),
        Token(tt.EOF, 4),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block(
                [
                    IfStmt(
                        Literal(True),
                        Block(
                            [
                                ExpressionStatement(Literal(1)),
                                ExpressionStatement(Literal(1)),
                            ]
                        ),
                    )
                ]
            ),
        )
    ]

    assert parser.parse() == expected


def test_nested_if_else():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "        "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.ELSE, 4, "else"),
        Token(tt.COLON, 4, ":"),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.INDENT, 5, "        "),
        Token(tt.NUMBER, 5, "2", 2),
        Token(tt.NEWLINE, 5, "\n"),
        Token(tt.DEDENT, 6),
        Token(tt.DEDENT, 6),
        Token(tt.ELSE, 6, "else"),
        Token(tt.COLON, 6, ":"),
        Token(tt.NEWLINE, 6, "\n"),
        Token(tt.INDENT, 7, "    "),
        Token(tt.NUMBER, 7, "3", 3),
        Token(tt.NEWLINE, 7, "\n"),
        Token(tt.DEDENT, 7),
        Token(tt.EOF, 7),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block(
                [
                    IfStmt(
                        Literal(True),
                        Block(
                            [
                                ExpressionStatement(Literal(1)),
                                ExpressionStatement(Literal(1)),
                            ]
                        ),
                        else_block=ElseBlock([ExpressionStatement(Literal(2))]),
                    )
                ]
            ),
            else_block=ElseBlock([ExpressionStatement(Literal(3))]),
        )
    ]

    assert parser.parse() == expected


def test_nested_if_elif():
    tokens = [
        Token(tt.IF, 1, "if"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.IF, 2, "if"),
        Token(tt.TRUE, 2, "True"),
        Token(tt.COLON, 2, ":"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.INDENT, 3, "        "),
        Token(tt.NUMBER, 3, "1", 1),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.NUMBER, 4, "1", 1),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 4),
        Token(tt.ELIF, 4, "else"),
        Token(tt.FALSE, 4, "False"),
        Token(tt.COLON, 4, ":"),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.INDENT, 5, "        "),
        Token(tt.NUMBER, 5, "2", 2),
        Token(tt.NEWLINE, 5, "\n"),
        Token(tt.DEDENT, 6),
        Token(tt.DEDENT, 6),
        Token(tt.ELIF, 6, "elif"),
        Token(tt.TRUE, 6, "True"),
        Token(tt.COLON, 6, ":"),
        Token(tt.NEWLINE, 6, "\n"),
        Token(tt.INDENT, 7, "    "),
        Token(tt.NUMBER, 7, "3", 3),
        Token(tt.NEWLINE, 7, "\n"),
        Token(tt.DEDENT, 7),
        Token(tt.EOF, 7),
    ]

    parser = Parser(tokens)

    expected = [
        IfStmt(
            Literal(True),
            Block(
                [
                    IfStmt(
                        Literal(True),
                        Block(
                            [
                                ExpressionStatement(Literal(1)),
                                ExpressionStatement(Literal(1)),
                            ]
                        ),
                        elif_stmt=ElifStmt(
                            Literal(False), Block([ExpressionStatement(Literal(2))])
                        ),
                    )
                ]
            ),
            elif_stmt=ElifStmt(Literal(True), Block([ExpressionStatement(Literal(3))])),
        )
    ]

    assert parser.parse() == expected


def test_and():
    tokens = [
        Token(tt.TRUE, 1, "True"),
        Token(tt.AND, 1, "and"),
        Token(tt.FALSE, 1, "False"),
        Token(tt.EOF, 1),
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(
            Logical(Literal(True), Token(tt.AND, 1, "and"), Literal(False))
        )
    ]

    assert parser.parse() == expected


def test_or():
    tokens = [
        Token(tt.TRUE, 1, "True"),
        Token(tt.OR, 1, "or"),
        Token(tt.FALSE, 1, "False"),
        Token(tt.EOF, 1),
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(
            Logical(Literal(True), Token(tt.OR, 1, "or"), Literal(False))
        )
    ]

    assert parser.parse() == expected


def test_multiple_ands():
    tokens = [
        Token(tt.TRUE, 1, "True"),
        Token(tt.AND, 1, "and"),
        Token(tt.FALSE, 1, "False"),
        Token(tt.AND, 1, "and"),
        Token(tt.FALSE, 1, "False"),
        Token(tt.EOF, 1),
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(
            Logical(
                Logical(Literal(True), Token(tt.AND, 1, "and"), Literal(False)),
                Token(tt.AND, 1, "and"),
                Literal(False),
            )
        )
    ]

    assert parser.parse() == expected


def test_while():
    tokens = [
        Token(tt.WHILE, 1, "while"),
        Token(tt.TRUE, 1, "True"),
        Token(tt.COLON, 1, ":"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.FALSE, 2, "False"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.ELSE, 3, "else"),
        Token(tt.COLON, 3, ":"),
        Token(tt.NEWLINE, 3, "\n"),
        Token(tt.INDENT, 4, "    "),
        Token(tt.TRUE, 4, "True"),
        Token(tt.NEWLINE, 4, "\n"),
        Token(tt.DEDENT, 5),
        Token(tt.EOF, 5),
    ]

    parser = Parser(tokens)

    expected = [
        WhileStmt(
            Literal(True),
            Block([ExpressionStatement(Literal(False))]),
            else_block=Block([ExpressionStatement(Literal(True))]),
        )
    ]

    assert parser.parse() == expected


def test_call_no_args():
    tokens = [
        Token(tt.IDENTIFIER, 1, "f"),
        Token(tt.LPAREN, 1, "("),
        Token(tt.RPAREN, 1, ")"),
        Token(tt.EOF, 1),
    ]

    parser = Parser(tokens)

    expected = [
        ExpressionStatement(
            Call(
                Variable(Token(tt.IDENTIFIER, 1, "f")),
                paren=Token(tt.RPAREN, 1, ")"),
            )
        )
    ]

    assert parser.parse() == expected


def test_call_args():
    tokens = [
        Token(tt.IDENTIFIER, 1, "f"),
        Token(tt.LPAREN, 1, "("),
        Token(tt.IDENTIFIER, 1, "a"),
        Token(tt.COMMA, 1, ","),
        Token(tt.IDENTIFIER, 1, "b"),
        Token(tt.COMMA, 1, ","),
        Token(tt.IDENTIFIER, 1, "c"),
        Token(tt.RPAREN, 1, ")"),
        Token(tt.EOF, 1),
    ]

    parser = Parser(tokens)

    expected = ExpressionStatement(
        Call(
            Variable(Token(tt.IDENTIFIER, 1, "f")),
            paren=Token(tt.RPAREN, 1, ")"),
            arguments=CommaExpression(
                [
                    Variable(Token(tt.IDENTIFIER, 1, "a")),
                    Variable(Token(tt.IDENTIFIER, 1, "b")),
                    Variable(Token(tt.IDENTIFIER, 1, "c")),
                ]
            ),
        )
    )

    assert parser.parse()[0] == expected


def test_end_of_file_block_without_newline():
    tokens = [
        Token(type=tt.IDENTIFIER, line=1, lexeme="i", literal=None),
        Token(type=tt.ASSIGN, line=1, lexeme="=", literal=None),
        Token(type=tt.NUMBER, line=1, lexeme="0", literal=0),
        Token(type=tt.NEWLINE, line=1, lexeme="\n", literal=None),
        Token(type=tt.WHILE, line=2, lexeme="while", literal=None),
        Token(type=tt.IDENTIFIER, line=2, lexeme="i", literal=None),
        Token(type=tt.LESSER, line=2, lexeme="<", literal=None),
        Token(type=tt.NUMBER, line=2, lexeme="5", literal=5),
        Token(type=tt.COLON, line=2, lexeme=":", literal=None),
        Token(type=tt.NEWLINE, line=2, lexeme="\n", literal=None),
        Token(type=tt.INDENT, line=3, lexeme="    ", literal=None),
        Token(type=tt.IDENTIFIER, line=3, lexeme="i", literal=None),
        Token(type=tt.ASSIGN, line=3, lexeme="=", literal=None),
        Token(type=tt.IDENTIFIER, line=3, lexeme="i", literal=None),
        Token(type=tt.PLUS, line=3, lexeme="+", literal=None),
        Token(type=tt.NUMBER, line=3, lexeme="1", literal=1),
        Token(type=tt.DEDENT, line=3, lexeme=None, literal=None),
        Token(type=tt.EOF, line=3, lexeme=None, literal=None),
    ]

    parser = Parser(tokens)

    expected = [
        AssignmentStatement(
            name=Token(type=tt.IDENTIFIER, line=1, lexeme="i", literal=None),
            expr=Literal(value=0),
        ),
        WhileStmt(
            condition=Binary(
                left=Variable(
                    name=Token(type=tt.IDENTIFIER, line=2, lexeme="i", literal=None)
                ),
                operator=Token(type=tt.LESSER, line=2, lexeme="<", literal=None),
                right=Literal(value=5),
            ),
            block=Block(
                statements=[
                    AssignmentStatement(
                        name=Token(
                            type=tt.IDENTIFIER, line=3, lexeme="i", literal=None
                        ),
                        expr=Binary(
                            left=Variable(
                                name=Token(
                                    type=tt.IDENTIFIER, line=3, lexeme="i", literal=None
                                )
                            ),
                            operator=Token(
                                type=tt.PLUS, line=3, lexeme="+", literal=None
                            ),
                            right=Literal(value=1),
                        ),
                    )
                ]
            ),
            else_block=None,
        ),
    ]

    assert parser.parse() == expected


def test_function_def():
    tokens = [
        Token(tt.DEF, 1, "def"),
        Token(tt.IDENTIFIER, 1, "f"),
        Token(tt.LPAREN, 1, "("),
        Token(tt.IDENTIFIER, 1, "a"),
        Token(tt.COMMA, 1, ","),
        Token(tt.IDENTIFIER, 1, "b"),
        Token(tt.RPAREN, 1, ")"),
        Token(tt.COLON, 1, ":"),
        Token(tt.NEWLINE, 1, "\n"),
        Token(tt.INDENT, 2, "    "),
        Token(tt.IDENTIFIER, 2, "a"),
        Token(tt.ASSIGN, 2, "="),
        Token(tt.IDENTIFIER, 2, "b"),
        Token(tt.NEWLINE, 2, "\n"),
        Token(tt.DEDENT, 3),
        Token(tt.EOF, 3),
    ]

    parser = Parser(tokens)

    expected = FunctionDefinition(
        name=Token(tt.IDENTIFIER, 1, "f"),
        params=[
            Variable(Token(tt.IDENTIFIER, 1, "a")),
            Variable(Token(tt.IDENTIFIER, 1, "b")),
        ],
        block=Block(
            statements=[
                AssignmentStatement(
                    name=Token(tt.IDENTIFIER, 2, "a"),
                    expr=Variable(Token(tt.IDENTIFIER, 2, "b")),
                )
            ]
        ),
    )

    assert parser.parse()[0] == expected
