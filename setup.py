#!/usr/bin/env python3

import pathlib
import re
import sys

from setuptools import setup

sys.path.insert(0, ".")
from DistUtilsExtra import __version__ as pkgversion


def get_debian_version() -> str:
    """Look what Debian version we have."""
    changelog = pathlib.Path(__file__).parent / "debian" / "changelog"
    with changelog.open("r", encoding="utf-8") as changelog_f:
        head = changelog_f.readline()
    match = re.compile(r".*\((.*)\).*").match(head)
    if not match:
        raise ValueError(f"Failed to extract Debian version from '{head}'.")
    return match.group(1)


def _check_debian_version() -> None:
    debian_version = get_debian_version()
    if not debian_version.startswith(pkgversion):
        print(
            f"Error: Debian version '{debian_version}' does not"
            f" start with DistUtilsExtra.__version__ '{pkgversion}'.",
            file=sys.stderr,
        )
        sys.exit(1)


_check_debian_version()

setup(
    name="python-distutils-extra",
    version=pkgversion,
    author="Sebastian Heinlein, Martin Pitt",
    author_email="sebi@glatzor.de, martin.pitt@ubuntu.com",
    description="Add support for i18n, documentation and icons to distutils",
    packages=["DistUtilsExtra", "DistUtilsExtra.command"],
    license="GNU GPL",
    platforms="posix",
    entry_points={
        "distutils.commands": [
            "build = DistUtilsExtra.command.build_extra:build_extra",
            "build_i18n = DistUtilsExtra.command.build_i18n:build_i18n",
            "build_icons = DistUtilsExtra.command.build_icons:build_icons",
            "build_help = DistUtilsExtra.command.build_help:build_help",
            "clean_i18n = DistUtilsExtra.command.clean_i18n:clean_i18n",
            "pylint = DistUtilsExtra.command.pylint:pylint",
        ]
    },
)
