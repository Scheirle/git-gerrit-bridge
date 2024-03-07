# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import packaging.version
import requests
import rich.console

from git_gerrit.__about__ import __version__

class Version:
    version = __version__

    @staticmethod
    def get_latest_version() -> str:
        try:
            r = requests.get("https://pypi.org/pypi/git-gerrit-bridge/json")
            return r.json()["info"]["version"]
        except:
            return Version.version

    @staticmethod
    def print_version_check():
        latest = packaging.version.parse(Version.get_latest_version())
        current = packaging.version.parse(Version.version)
        if current < latest:
            console = rich.console.Console()
            console.print()
            console.print(
                (" [red]![/] New version of [turquoise2]git gerrit[/] available: "
                f"{latest} (Currently installed {current})"))
