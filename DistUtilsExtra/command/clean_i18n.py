"""distutils_extra.command.clean_i18n

Implements the Distutils 'clean_i18n' command."""

# TODO: Address following pylint complaints
# pylint: disable=eval-used,missing-function-docstring

import logging
import os
import os.path
import pathlib
import shutil
import typing

from setuptools import Command, Distribution


def _log_error(unused_function: typing.Any, path: str, excinfo: typing.Tuple) -> None:
    logger = logging.getLogger(__name__)
    logger.warning("error removing %s: %s", path, excinfo[1])


# pylint: disable-next=invalid-name
class clean_i18n(Command):
    """clean up files generated by build_i18n"""

    description = __doc__
    user_options = [
        ("build-base=", "b", "base build directory (default: 'build.build-base')"),
        (
            "build-lib=",
            None,
            "build directory for all modules (default: 'build.build-lib')",
        ),
    ]

    def __init__(self, dist: Distribution, **kwargs: dict[str, typing.Any]) -> None:
        super().__init__(dist, **kwargs)
        self.distribution = dist
        self.initialize_options()

    def initialize_options(self) -> None:
        self.build_base: typing.Optional[str] = None

    def finalize_options(self) -> None:
        self.set_undefined_options("build", ("build_base", "build_base"))

    def run(self) -> None:
        """Clean up files generated by build_i18n."""
        assert self.build_base
        # clean build/mo
        mo_dir = os.path.join(self.build_base, "mo")
        if os.path.isdir(mo_dir):
            shutil.rmtree(mo_dir, onerror=_log_error)

        # clean built i18n files
        for setname in (
            "xml_files",
            "desktop_files",
            "schemas_files",
            "rfc822deb_files",
            "ba_files",
            "key_files",
        ):
            file_set = eval(
                self.distribution.get_option_dict("build_i18n").get(
                    setname, (None, "[]")
                )[1]
            )
            for target, files in file_set:
                build_target = os.path.join(self.build_base, target)
                for file in files:
                    if file.endswith(".in"):
                        file_merged = os.path.basename(file[:-3])
                    else:
                        file_merged = os.path.basename(file)
                    file_merged = pathlib.Path(build_target) / file_merged
                    file_merged.unlink(missing_ok=True)
                if os.path.exists(build_target):
                    os.removedirs(build_target)
