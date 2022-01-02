from __future__ import annotations

import builtins

from exc import NameNotFoundException


class Environment(dict):
    def __init__(self, enclosing: Environment = None):
        super().__init__()
        self.enclosing = enclosing

    def __setitem__(self, key, value) -> None:
        if self.enclosing:
            self.enclosing.__setitem__(key, value)
        else:
            return super().__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except NameNotFoundException:
            if self.enclosing:
                return self.enclosing.__getitem__(key)
            else:
                raise

    def __missing__(self, key):
        raise NameNotFoundException(f"name '{key}' is not defined")


def global_env():
    env = Environment()
    for name in dir(builtins):
        if not name.startswith("__"):
            env[name] = getattr(builtins, name)
    return env
