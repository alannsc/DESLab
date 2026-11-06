"""Compatibility entry point; package metadata lives in pyproject.toml."""

from setuptools import setup


if __name__ == "__main__":
    # Keep build output separate from the tracked build/ directory so pip
    # cannot include stale copies of modules.
    setup(options={"build": {"build_base": ".deslab-build"}})
