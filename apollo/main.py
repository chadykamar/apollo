#!/usr/bin/env python


import argparse
import sys
from exc import ParseException
from parser import Parser

from scanner import Scanner
from tok import TokenType as tt


class Interpreter:

    """
    Main class of our interpreter

    Attributes
    ----------
    error : bool
        True if an error was encountered during execution
    """

    def __init__(self) -> None:
        self.error = False

    def entrypoint(self):

        parser = argparse.ArgumentParser()

        parser.add_argument("script", nargs="?")

        ns = parser.parse_args()

        if ns.script:
            self.run_file(ns.script)
        else:
            self.repl()

    def repl(self):

        while True:
            line = input("apollo> ")
            if line:
                self.run(line)
            else:
                break

    def run_file(self, filename):

        try:
            with open(filename, "r") as f:
                self.run(f.read())
        except FileNotFoundError:
            print(f"file {filename} was not found", file=sys.stderr)
            sys.exit(2)

    def run(self, code: str):
        scanner = Scanner(code)

        tokens = scanner.scan_tokens()

        parser = Parser(tokens)

        match parser.parse():
            case ParseException(msg, token) as e:
                self.report(token, msg)
                raise e
            case expr:
                import pprint
                pprint.pprint(expr)

    def report(self, token, msg):
        match token.type:
            case tt.EOF: print(f"[line {token.line}] Error at end: {msg}")
            case _: print(f"[line {token.line}] Error at {token.lexeme}: {msg}")
        self.error = True


if __name__ == "__main__":
    Interpreter().entrypoint()
