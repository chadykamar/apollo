from tok.tok import Token


class UnexpectedCharacter(Exception):
    pass


class UnterminatedString(Exception):
    pass


class ApolloException(Exception):
    def __init__(self, msg, token: Token):
        super().__init__(msg)
        self.token = token


class ParseException(ApolloException):
    pass


class RuntimeException(ApolloException):
    pass


class NameNotFoundException(Exception):
    pass


class ReturnException(ApolloException):
    def __init__(self, msg, token, value):
        super().__init__(msg, token)
        self.value = value
