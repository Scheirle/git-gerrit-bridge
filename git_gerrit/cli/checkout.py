# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli

from git_gerrit.utils.gerrit import Gerrit
from git_gerrit.utils.git import GitConfig, git

class Checkout(plumbum.cli.Application):
    '''
    Downloads the change with the given <number> from gerrit and creates branch <name>.
    '''

    def main(self, number, name=None):
        changes = Gerrit.get_remote_changes(f"change:{number} limit:1")
        if len(changes) != 1:
            print("Change not found")
            return
        change = changes[0]
        if name is None:
            name = change.recommend_branch_name()

        git["fetch", GitConfig.remote(), change.gerrit_ref].run_fg()
        git["branch", name, "FETCH_HEAD"].run_fg() # create new branch
        git["branch", "--set-upstream-to", f"{GitConfig.remote()}/{change.branch_remote}", name].run_fg()
        git["switch", name].run_fg()
