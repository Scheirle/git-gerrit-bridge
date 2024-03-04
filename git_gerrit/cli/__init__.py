# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli

from git_gerrit.__about__ import __version__
from git_gerrit.utils.git import GitConfig

class GitGerrit(plumbum.cli.Application):
    PROGNAME = "git gerrit"
    VERSION = __version__

    def main(self):
        if not GitConfig.repo_in_current_working_directory():
            print("Not in a git directory")
            return 1

        if not self.nested_command:
            self.help()
            return 1

for command in ["New", "Checkout", "Push", "Clean", "Rebase", "Status", "Sync"]:
    name = command.lower()
    GitGerrit.subcommand(name, f"git_gerrit.cli.{name}.{command}")
