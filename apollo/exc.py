from tok.tok import Token


class UnexpectedCharacter(Exception):
    pass


class UnterminatedString(Exception):
    pass


class ParseException(Exception):

    def __init__(self, msg, token: Token):
        super().__init__(msg)
        self.token = token
