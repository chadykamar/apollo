
import pytest
from exc import RuntimeException
from expression import Binary, Grouping, Literal, Ternary, Unary
from interpreter import Interpreter
from tok import Token
from tok import TokenType as tt


@pytest.mark.parametrize(
    ['expression', 'result'], [
        (Literal(1), 1),
        (Literal(0.5), 0.5),
        (Literal(True), True),
        (Literal(False), False),
        (Literal("hello"), "hello"),
        (Literal(None), None),
    ]
)
def test_literal(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret(expression) == result


@pytest.mark.parametrize(
    ['expression', 'result'], [
        (Ternary(left=Literal(1), if_=Token(tt.IF, 1, 'if'), condition=Literal(
            True), else_=Token(tt.ELSE, 1, 'else'), right=Literal(5)), 1),
        (Ternary(left=Literal(1), if_=Token(tt.IF, 1, 'if'), condition=Literal(
            False), else_=Token(tt.ELSE, 1, 'else'), right=Literal(5)), 5),
    ]
)
def test_ternary(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret(expression) == result


def test_grouping():

    expr = Binary(left=Literal(10), operator=Token(tt.STAR, 1, "*"), right=Grouping(Binary(left=Literal(1), operator=Token(
        tt.PLUS, 1, "+"), right=Literal(5))))

    interpreter = Interpreter()
    assert interpreter.interpret(expr) == 60


@ pytest.mark.parametrize(
    ['expression', 'result'], [
        (Binary(left=Literal(1), operator=Token(tt.PLUS, 1, "+"), right=Literal(5)), 6),
        (Binary(left=Literal(5), operator=Token(tt.MINUS, 1, "-"), right=Literal(1)), 4),
        (Binary(left=Literal(5), operator=Token(tt.STAR, 1, "*"), right=Literal(2)), 10),
        (Binary(left=Literal(1), operator=Token(
            tt.SLASH, 1, "/"), right=Literal(2)), 0.5),
        (Binary(left=Literal(1), operator=Token(
            tt.GREATER, 1, ">"), right=Literal(0)), True),
        (Binary(left=Literal(1), operator=Token(
            tt.LESSER, 1, "<"), right=Literal(0)), False),
        (Binary(left=Literal(1), operator=Token(
            tt.LEQUAL, 1, "<="), right=Literal(1)), True),
        (Binary(left=Literal(1), operator=Token(
            tt.LEQUAL, 1, "<="), right=Literal(0)), False),
        (Binary(left=Literal(2), operator=Token(
            tt.GEQUAL, 1, ">="), right=Literal(1)), True),
        (Binary(left=Literal(1), operator=Token(
            tt.GEQUAL, 1, ">="), right=Literal(1)), True),
        (Binary(left=Literal(1), operator=Token(
            tt.EQUAL, 1, "=="), right=Literal(1)), True),
        (Binary(left=Literal(1), operator=Token(
            tt.EQUAL, 1, "=="), right=Literal(2)), False),
        (Binary(left=Literal(1), operator=Token(
            tt.NEQUAL, 1, "!="), right=Literal(1)), False),
        (Binary(left=Literal(1), operator=Token(
            tt.NEQUAL, 1, "!="), right=Literal(2)), True),
    ]
)
def test_binary(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret(expression) == result


@ pytest.mark.parametrize(
    ['expression', 'result'], [
        (Unary(operator=Token(tt.NOT, 1, "not"), right=Literal(True)), False),
        (Unary(operator=Token(tt.MINUS, 1, "-"), right=Literal(1)), -1),

    ]
)
def test_unary(expression, result):
    interpreter = Interpreter()
    assert interpreter.interpret(expression) == result


def test_type_error():

    expr = Binary(left=Literal(1), operator=Token(
        tt.PLUS, 1, "+"), right=Literal("hello"))

    interpreter = Interpreter()

    with pytest.raises(RuntimeException) as e:
        interpreter.interpret(expr)
        assert "TypeError" in e


def test_div_zero():

    expr = Binary(left=Literal(1), operator=Token(
        tt.SLASH, 1, "/"), right=Literal(0))

    interpreter = Interpreter()

    with pytest.raises(RuntimeException) as e:
        interpreter.interpret(expr)
        assert "ZeroDivisionError" in e
