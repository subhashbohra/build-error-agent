﻿import os


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)
