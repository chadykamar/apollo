#!/usr/bin/env python


import argparse
import sys
from parser import Parser

from exc import ParseException, RuntimeException
from interpreter import Interpreter
from scanner import Scanner
from tok import TokenType as tt
from tok.tok import Token


class Apollo:

    """
    Front-facing class of the interpreter

    Attributes
    ----------
    error : bool
        True if an error was encountered during execution
    """

    def __init__(self) -> None:
        self.error = False
        self.runtime_error = False
        self.interpreter = Interpreter()

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

                try:
                    self.run(line)
                except RuntimeException as e:
                    self.report(e.token, str(e))
            else:
                break

    def run_file(self, filename):

        try:
            with open(filename, "r") as f:
                self.run(f.read())
        except FileNotFoundError:
            print(f"file {filename} was not found", file=sys.stderr)
            sys.exit(2)
        except RuntimeException as e:
            self.report(e.token, str(e))
            self.runtime_error = True
            raise

    def run(self, code: str):

        try:
            scanner = Scanner(code)
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            statements = parser.parse()
            results = self.interpreter.interpret(statements)

        except ParseException as e:
            self.report(e.token, str(e))

    def report(self, token: Token, msg):
        match token.type:
            case tt.EOF: print(f"[line {token.line}] Error at end: {msg}")
            case _: print(f"[line {token.line}] Error at {token.type} {token.lexeme}: {msg}")
        self.error = True

if __name__ == "__main__":
    Apollo().entrypoint()
