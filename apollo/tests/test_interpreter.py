import pytest
from exc import NameNotFoundException, RuntimeException
from expression import Binary, Grouping, Literal, Ternary, Unary, Variable
from interpreter import Interpreter
from statement import AssignmentStatement, Block, ElifStmt, ElseBlock, ExpressionStatement, IfStmt
from tok import Token
from tok import TokenType as tt


@pytest.mark.parametrize(['statement', 'result'], [
    (ExpressionStatement(Literal(1)), 1),
    (ExpressionStatement(Literal(0.5)), 0.5),
    (ExpressionStatement(Literal(True)), True),
    (ExpressionStatement(Literal(False)), False),
    (ExpressionStatement(Literal("hello")), "hello"),
    (ExpressionStatement(Literal(None)), None),
])
def test_literal(statement, result):
    interpreter = Interpreter()
    assert interpreter.interpret([statement]) == [result]


@pytest.mark.parametrize(['statement', 'result'], [
    (ExpressionStatement(
        Ternary(left=Literal(1),
                if_=Token(tt.IF, 1, 'if'),
                condition=Literal(True),
                else_=Token(tt.ELSE, 1, 'else'),
                right=Literal(5))), 1),
    (ExpressionStatement(
        Ternary(left=Literal(1),
                if_=Token(tt.IF, 1, 'if'),
                condition=Literal(False),
                else_=Token(tt.ELSE, 1, 'else'),
                right=Literal(5))), 5),
])
def test_ternary(statement, result):
    interpreter = Interpreter()
    assert interpreter.interpret([statement]) == [result]


def test_grouping():

    expr = ExpressionStatement(
        Binary(left=Literal(10),
               operator=Token(tt.STAR, 1, "*"),
               right=Grouping(
                   Binary(left=Literal(1),
                          operator=Token(tt.PLUS, 1, "+"),
                          right=Literal(5)))))

    interpreter = Interpreter()
    assert interpreter.interpret([expr]) == [60]


@pytest.mark.parametrize(['expression', 'result'], [
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.PLUS, 1, "+"),
               right=Literal(5))), 6),
    (ExpressionStatement(
        Binary(left=Literal(5),
               operator=Token(tt.MINUS, 1, "-"),
               right=Literal(1))), 4),
    (ExpressionStatement(
        Binary(left=Literal(5),
               operator=Token(tt.STAR, 1, "*"),
               right=Literal(2))), 10),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.SLASH, 1, "/"),
               right=Literal(2))), 0.5),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.GREATER, 1, ">"),
               right=Literal(0))), True),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.LESSER, 1, "<"),
               right=Literal(0))), False),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.LEQUAL, 1, "<="),
               right=Literal(1))), True),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.LEQUAL, 1, "<="),
               right=Literal(0))), False),
    (ExpressionStatement(
        Binary(left=Literal(2),
               operator=Token(tt.GEQUAL, 1, ">="),
               right=Literal(1))), True),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.GEQUAL, 1, ">="),
               right=Literal(1))), True),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.EQUAL, 1, "=="),
               right=Literal(1))), True),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.EQUAL, 1, "=="),
               right=Literal(2))), False),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.NEQUAL, 1, "!="),
               right=Literal(1))), False),
    (ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.NEQUAL, 1, "!="),
               right=Literal(2))), True),
])
def test_binary(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret([expression]) == [result]


@pytest.mark.parametrize(['expression', 'result'], [
    (ExpressionStatement(
        Unary(operator=Token(tt.NOT, 1, "not"), right=Literal(True))), False),
    (ExpressionStatement(
        Unary(operator=Token(tt.MINUS, 1, "-"), right=Literal(1))), -1),
])
def test_unary(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret([expression]) == [result]


def test_type_error():

    expr = ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.PLUS, 1, "+"),
               right=Literal("hello")))

    interpreter = Interpreter()

    with pytest.raises(RuntimeException) as e:
        interpreter.interpret([expr])
        assert "TypeError" in e


def test_div_zero():

    expr = ExpressionStatement(
        Binary(left=Literal(1),
               operator=Token(tt.SLASH, 1, "/"),
               right=Literal(0)))

    interpreter = Interpreter()

    with pytest.raises(RuntimeException) as e:
        interpreter.interpret([expr])
        assert "ZeroDivisionError" in e


def test_assignment():

    interpreter = Interpreter()

    statements = [
        AssignmentStatement(Token(tt.IDENTIFIER, 1, 'a'), Literal(1))
    ]

    interpreter.interpret(statements)

    assert interpreter.env['a'] == 1


def test_variable():

    interpreter = Interpreter()

    interpreter.env['b'] = 1

    statements = [ExpressionStatement(Variable(Token(tt.IDENTIFIER, 2, 'b')))]

    assert interpreter.interpret(statements) == [1]


def test_name_not_found():

    interpreter = Interpreter()

    statements = [ExpressionStatement(Variable(Token(tt.IDENTIFIER, 1, 'b')))]

    with pytest.raises(NameNotFoundException):
        interpreter.interpret(statements)


def test_if_stmt():

    interpreter = Interpreter()

    statements = [
        IfStmt(
            Literal(True),
            Block([
                AssignmentStatement(
                    Token(tt.IDENTIFIER, 2, lexeme="a"),
                    Binary(Literal(1), Token(tt.PLUS, 2, "+"), Literal(1)))
            ]))
    ]

    interpreter.interpret(statements)

    assert interpreter.env["a"] == 2


def test_if_stmt_multiple_stmt_block():

    interpreter = Interpreter()

    statements = [
        IfStmt(
            Literal(True),
            Block([
                AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"), Literal(1)),
                AssignmentStatement(Token(tt.IDENTIFIER, 2, "b"), Literal(10)),
            ]))
    ]

    interpreter.interpret(statements)

    assert interpreter.env['a'] == 1 and interpreter.env['b'] == 10


@pytest.mark.parametrize("if_cond, elif_cond, expected", [(True, False, 1),
                                                          (False, True, 2)])
def test_if_elif(if_cond, elif_cond, expected):

    interpreter = Interpreter()

    statements = [
        IfStmt(Literal(if_cond),
               Block([
                   AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                       Literal(1))
               ]),
               elif_stmt=ElifStmt(
                   Literal(elif_cond),
                   Block([
                       AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                           Literal(2))
                   ])))
    ]

    interpreter.interpret(statements)

    assert interpreter.env['a'] == expected


@pytest.mark.parametrize("if_cond, expected", [(True, 1), (False, 2)])
def test_if_else(if_cond, expected):

    interpreter = Interpreter()

    statements = [
        IfStmt(Literal(if_cond),
               Block([
                   AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                       Literal(1))
               ]),
               else_block=ElseBlock([
                   AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                       Literal(2))
               ]))
    ]

    interpreter.interpret(statements)

    assert interpreter.env['a'] == expected


@pytest.mark.parametrize("i, j, expected", [(0, 0, 10000), (1, 0, 1000),
                                            (-1, 0, 1), (-1, 1, 10),
                                            (-1, -1, 100)])
def test_nested_if_elif_else(i, j, expected):

    interpreter = Interpreter()

    statements = [
        IfStmt(
            Literal(i < 0),
            Block([
                IfStmt(Literal(j == 0),
                       Block([
                           AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                               Literal(1))
                       ]),
                       elif_stmt=ElifStmt(Literal(j > 0),
                                          Block([
                                              AssignmentStatement(
                                                  Token(tt.IDENTIFIER, 2, "a"),
                                                  Literal(10))
                                          ]),
                                          else_block=ElseBlock([
                                              AssignmentStatement(
                                                  Token(tt.IDENTIFIER, 2, "a"),
                                                  Literal(100))
                                          ])))
            ]),
            elif_stmt=ElifStmt(
                Literal(i > 0),
                Block([
                    AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                        Literal(1000))
                ]),
                else_block=ElseBlock([
                    AssignmentStatement(Token(tt.IDENTIFIER, 2, "a"),
                                        Literal(10000))
                ])),
        )
    ]

    interpreter.interpret(statements)

    assert interpreter.env['a'] == expected


@pytest.mark.parametrize("left, right, expected", [(True, False, False),
                                                   (True, True, True),
                                                   (False, False, False),
                                                   (1, 0, 1), (0, 1, 0)])
def test_and(left, right, expected):

    expression = Logical(Literal(0), Token(tt.AND, 1, "and"), Literal(1))

    interpreter = Interpreter()

    assert interpreter.evaluate(expression) == 0


@pytest.mark.parametrize("left, right, expected", [(True, False, True),
                                                   (True, True, True),
                                                   (False, False, False),
                                                   (1, 0, 1), (0, 1, 1)])
def test_or(left, right, expected):

    expression = Logical(Literal(left), Token(tt.OR, 1, "or"), Literal(right))

    interpreter = Interpreter()

    assert interpreter.evaluate(expression) == expected
