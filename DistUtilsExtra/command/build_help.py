"""Implement the Distutils "build_help" command."""

# TODO: Address following pylint complaints
# pylint: disable=attribute-defined-outside-init,missing-function-docstring

import os.path
from glob import glob

from setuptools import Command


# pylint: disable-next=invalid-name
class build_help(Command):
    """install Mallard or DocBook XML based documentation"""

    description = __doc__
    user_options = [("help-dir", None, "help directory in the source tree")]

    def initialize_options(self):
        self.help_dir = None

    def finalize_options(self):
        if self.help_dir is None:
            self.help_dir = "help"

    def get_data_files(self):
        data_files = []
        name = self.distribution.metadata.name

        for path in glob(os.path.join(self.help_dir, "*")):
            lang = os.path.basename(path)
            path_xml = os.path.join("share/help", lang, name)
            path_figures = os.path.join("share/help", lang, name, "figures")

            docbook_files = glob(f"{path}/index.docbook")
            docbook_files_extra = glob(f"{path}/*.xml")
            mallard_files = glob(f"{path}/*.page")
            data_files.append(
                (path_xml, docbook_files + docbook_files_extra + mallard_files)
            )
            data_files.append((path_figures, glob(f"{path}/figures/*.png")))

        return data_files

    def run(self):
        self.announce("Setting up help files...")

        data_files = self.distribution.data_files
        data_files.extend(self.get_data_files())
