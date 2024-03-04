# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli

from git_gerrit.utils.git import GitConfig, git

class New(plumbum.cli.Application):
    """ Creates a new branch tracking <upstream> with the name <name>."""

    def main(self, upstream, name):
        git["checkout", "-b", name, f"{GitConfig.remote()}/{upstream}"].run_fg()
