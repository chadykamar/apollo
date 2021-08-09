from enum import Enum, auto


class TokenType(Enum):

    # Grouping
    LPAREN = auto()
    RPAREN = auto()
    LBRACK = auto()
    RBRACK = auto()
    LBRACE = auto()
    RBRACE = auto()
    LCHEV = auto()
    RCHEV = auto()

    DOT = auto()
    COMMA = auto()
    COLON = auto()
    SCOLON = auto()

    # Arithmetic
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    ASSIGN = auto()

    # Comparison
    EQUAL = auto()
    NEQUAL = auto()
    LESSER = LCHEV
    LEQUAL = auto()
    GREATER = RCHEV
    GEQUAL = auto()

    BSLASH = auto()
    AMPER = auto()
    PIPE = auto()

    BANG = auto()
    QUESTION = auto()

    QUOTE = auto()
    SQUOTE = auto()
    BQUOTE = auto()

    # Keywords

    # Loop
    FOR = auto()
    WHILE = auto()
    DO = auto()

    # Definitions
    DEF = auto()
    CLASS = auto()
    RETURN = auto()
    SELF = auto()
    IMPORT = auto()

    # Bool
    AND = auto()
    OR = auto()
    NOT = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()

    HASH = auto()

    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # End of file
    EOF = auto()
