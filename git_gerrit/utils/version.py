# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import packaging.version
import requests
import rich.console

from git_gerrit.__about__ import __version__
from git_gerrit.utils.git import git

class Version:
    version = __version__
    config_key = "git-gerrit-bridge.last-version-check"

    @staticmethod
    def get_latest_version() -> str:
        try:
            r = requests.get("https://pypi.org/pypi/git-gerrit-bridge/json")
            return r.json()["info"]["version"]
        except:
            return Version.version

    @staticmethod
    def get_last_check():
        time = git["config", "--global", "--default", "0", "--get", Version.config_key]()
        return datetime.datetime.fromtimestamp(int(time)).date()

    @staticmethod
    def set_last_check():
        git["config", "--global", Version.config_key,
            str(int(datetime.datetime.today().timestamp()))]()

    @staticmethod
    def check_version() -> str|None:
        if datetime.datetime.today().date() == Version.get_last_check():
            return None
        current = packaging.version.parse(Version.version)
        latest = packaging.version.parse(Version.get_latest_version())
        if current < latest:
            return f"{latest}"
        Version.set_last_check()
        return None

    @staticmethod
    def print_version_check():
        new_version = Version.check_version()
        if new_version:
            console = rich.console.Console()
            console.print()
            console.print(
                (" [red]![/] New version of [turquoise2]git gerrit[/] available: "
                f"{new_version} (Currently installed {Version.version})"))
