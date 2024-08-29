"""distutils_extra.command.build_i18n

Implements the Distutils 'build_i18n' command."""

# TODO: Address following pylint complaints
# pylint: disable=attribute-defined-outside-init,broad-except,eval-used,missing-function-docstring

import glob
import os
import pathlib

from setuptools import Command


# pylint: disable-next=invalid-name,too-many-instance-attributes
class build_i18n(Command):
    """integrate the gettext framework"""

    description = __doc__

    user_options = [
        ("desktop-files=", None, ".desktop.in files that should be merged"),
        ("xml-files=", None, ".xml.in files that should be merged"),
        ("schemas-files=", None, ".schemas.in files that should be merged"),
        ("ba-files=", None, "bonobo-activation files that should be merged"),
        ("rfc822deb-files=", None, "RFC822 files that should be merged"),
        ("key-files=", None, ".key.in files that should be merged"),
        ("domain=", "d", "gettext domain"),
        ("merge-po", "m", "merge po files against template"),
        ("po-dir=", "p", "directory that holds the i18n files"),
        ("bug-contact=", None, "contact address for msgid bugs"),
    ]

    boolean_options = ["merge-po"]

    def initialize_options(self):
        self.desktop_files = []
        self.xml_files = []
        self.key_files = []
        self.schemas_files = []
        self.ba_files = []
        self.rfc822deb_files = []
        self.domain = None
        self.merge_po = False
        self.bug_contact = None
        self.po_dir = None

    def finalize_options(self):
        if self.domain is None:
            self.domain = self.distribution.metadata.name
        if self.po_dir is None:
            self.po_dir = "po"

    def run(self):
        """
        Update the language files, generate mo files and add them
        to the to be installed files
        """
        # TODO: split into smaller methods
        # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        if not os.path.isdir(self.po_dir):
            return

        data_files = self.distribution.data_files
        if data_files is None:
            # in case not data_files are defined in setup.py
            self.distribution.data_files = data_files = []

        if self.bug_contact is not None:
            os.environ["XGETTEXT_ARGS"] = f"--msgid-bugs-address={self.bug_contact} "

        # Print a warning if there is a Makefile that would overwrite our
        # values
        if os.path.exists(f"{self.po_dir}/Makefile"):
            self.announce(
                """
WARNING: Intltool will use the values specified from the
         existing po/Makefile in favor of the values
         from setup.cfg.
         Remove the Makefile to avoid problems."""
            )

        # If there is a po/LINGUAS file, or the LINGUAS environment variable
        # is set, only compile the languages listed there.
        selected_languages = None
        linguas_file = pathlib.Path(self.po_dir) / "LINGUAS"
        if linguas_file.is_file():
            selected_languages = linguas_file.read_text().split()
        if "LINGUAS" in os.environ:
            selected_languages = os.environ["LINGUAS"].split()

        # Update po(t) files and print a report
        # We have to change the working dir to the po dir for intltool
        cmd = ["intltool-update", (self.merge_po and "-r" or "-p"), "-g", self.domain]
        cwd = os.getcwd()
        os.chdir(self.po_dir)
        self.spawn(cmd)
        os.chdir(cwd)
        max_po_mtime = 0
        for po_file in glob.glob(f"{self.po_dir}/*.po"):
            lang = os.path.basename(po_file[:-3])
            if selected_languages and lang not in selected_languages:
                continue
            mo_dir = os.path.join("build", "mo", lang, "LC_MESSAGES")
            mo_file = os.path.join(mo_dir, f"{self.domain}.mo")
            if not os.path.exists(mo_dir):
                os.makedirs(mo_dir)
            cmd = ["msgfmt", po_file, "-o", mo_file]
            po_mtime = os.path.getmtime(po_file)
            mo_mtime = os.path.exists(mo_file) and os.path.getmtime(mo_file) or 0
            if po_mtime > max_po_mtime:
                max_po_mtime = po_mtime
            if po_mtime > mo_mtime:
                self.spawn(cmd)

            targetpath = os.path.join("share/locale", lang, "LC_MESSAGES")
            data_files.append((targetpath, (mo_file,)))

        # merge .in with translation
        for option, switch in (
            (self.xml_files, "-x"),
            (self.desktop_files, "-d"),
            (self.schemas_files, "-s"),
            (self.rfc822deb_files, "-r"),
            (self.ba_files, "-b"),
            (self.key_files, "-k"),
        ):
            try:
                file_set = eval(option)
            except Exception:
                continue
            for target, files in file_set:
                build_target = os.path.join("build", target)
                if not os.path.exists(build_target):
                    os.makedirs(build_target)
                files_merged = []
                for file in files:
                    if file.endswith(".in"):
                        file_merged = os.path.basename(file[:-3])
                    else:
                        file_merged = os.path.basename(file)
                    file_merged = os.path.join(build_target, file_merged)
                    cmd = ["intltool-merge", switch, self.po_dir, file, file_merged]
                    mtime_merged = (
                        os.path.exists(file_merged)
                        and os.path.getmtime(file_merged)
                        or 0
                    )
                    mtime_file = os.path.getmtime(file)
                    if mtime_merged < max_po_mtime or mtime_merged < mtime_file:
                        # Only build if output is older than input (.po,.in)
                        self.spawn(cmd)
                    files_merged.append(file_merged)
                data_files.append((target, files_merged))


# class build
