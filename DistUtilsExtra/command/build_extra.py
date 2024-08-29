import setuptools.command.build


# pylint: disable-next=invalid-name
class build_extra(setuptools.command.build.build):
    """Adds the extra commands to the build target. This class should be
    used with setuptools."""

    def __init__(self, dist):
        super().__init__(dist)

        self.user_options.extend(
            [
                ("i18n", None, "use the localisation"),
                ("icons", None, "use icons"),
                ("kdeui", None, "use kdeui"),
                ("help", None, "use help system"),
            ]
        )

    def initialize_options(self):
        super().initialize_options()
        self.i18n = False
        self.icons = False
        self.help = False
        self.kdeui = False

    def finalize_options(self):
        def has_help(unused_command):
            return self.help == "True" or (
                "build_help" in self.distribution.cmdclass and self.help != "False"
            )

        def has_icons(unused_command):
            return self.icons == "True" or (
                "build_icons" in self.distribution.cmdclass and self.help != "False"
            )

        def has_i18n(unused_command):
            return self.i18n == "True" or (
                "build_i18n" in self.distribution.cmdclass and self.i18n != "False"
            )

        def has_kdeui(unused_command):
            return self.kdeui == "True" or (
                "build_kdeui" in self.distribution.cmdclass and self.kdeui != "False"
            )

        super().finalize_options()
        self.sub_commands.append(("build_i18n", has_i18n))
        self.sub_commands.append(("build_icons", has_icons))
        self.sub_commands.append(("build_help", has_help))
        self.sub_commands.insert(
            0, ("build_kdeui", has_kdeui)
        )  # need to run before build_py
