# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli
import rich

from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.git import git

class Rebase(plumbum.cli.Application):
    '''Interactive rebase local changes without rebasing onto remote.'''

    def main(self):
        console = rich.console.Console()
        b = LocalBranch.from_head()
        num_changes = len(b.get_changes())
        if num_changes == 0:
            print("Nothing to rebase")
            return
        console.print(f"Starting interactive rebase of [magenta1]{b.local_name}[/] with {num_changes} Changes...")
        git["rebase", "-i", f"HEAD~{num_changes}"].run_fg()
