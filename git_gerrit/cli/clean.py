# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli
import rich.console
import rich.live
import rich.table
import rich.text

from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.change import Change
from git_gerrit.utils.git import git

class Clean(plumbum.cli.Application):
    '''Removes all local branches where all commits are already merged in gerrit.'''

    def do_action(self, branch: LocalBranch):
        if not branch.has_remote():
            return ("?", "Skipped (no remote set)", "red")

        changes = branch.get_changes()
        commits = len(changes)
        for local_change in changes:
            change = Change.from_local(local_change)
            if not change.remote:
                return (commits, "Skipped (Not yet pushed)", "dark_turquoise")
            if not change.remote.is_merged() and not change.remote.is_abandoned():
                return (commits, "Skipped (Not yet merged)", "green")

        (rc, _, stderr) = git["branch", "-D", branch.local_name].run(retcode=None)
        if rc == 0:
            return (commits, "Deleted", "turquoise2")
        return (commits, f"Deletion failed: {stderr.strip()}", "red")

    def main(self):
        console = rich.console.Console()
        console.print(f"Cleaning {len(LocalBranch.get_branches())} branches:")
        with rich.live.Live(auto_refresh=False) as live:
            grid = rich.table.Table.grid(padding=(0,1))
            grid.add_column()
            grid.add_column()
            grid.add_column()
            for branch in LocalBranch.get_branches():
                num_commits, msg, style = self.do_action(branch)
                grid.add_row(
                    rich.text.Text(f"{branch.local_name}", "magenta1"),
                    f"{num_commits} Commits",
                    rich.text.Text(msg, style))
                live.update(grid, refresh=True)
