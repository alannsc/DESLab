"""Compatibility entry point; package metadata lives in pyproject.toml."""

from setuptools import setup


if __name__ == "__main__":
    # The original repository tracks build/; use a separate cache so pip cannot
    # include stale copies of modules from that directory.
    setup(options={"build": {"build_base": ".deslab-build"}})
