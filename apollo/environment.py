from exc import NameNotFoundException
from tok.tok import Token
from collections import UserDict


class Environment(dict):

    def __init__(self):
        super().__init__()

    def __missing__(self, key):
        raise NameNotFoundException(f"name '{key}' is not defined")
