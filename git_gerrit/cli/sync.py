# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli
import rich.console

from rich import print
from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.change import Change
from git_gerrit.utils.localchange import LocalChange
from git_gerrit.utils.git import GitConfig, git

class Sync(plumbum.cli.Application):
    '''Interactive rebase the current branch and picks either the local or remote change which ever is more recent'''

    def fetch_and_get_hash(self, local_change: LocalChange):
        change = Change.from_local(local_change)
        if change.remote and change.remote.hash != local_change.hash and change.remote.update > local_change.update:
            git["fetch", GitConfig.remote(), f"{change.remote.gerrit_ref}"].run_fg()
            return (True, change.remote.hash)
        return (False, local_change.hash)

    def main(self):
        console = rich.console.Console()
        b = LocalBranch.from_head()
        if b is None:
            print("Current branch not known, no branch checked out?")
            return 1
        if not LocalBranch.is_head_clean():
            print(f"[magenta1]{b.local_name}[/] contains uncommited changes, aborting.")
            return 1
        changes = b.get_changes()
        console.print(f"Preparing interactive rebase of [magenta1]{b.local_name}[/] with {len(changes)} Changes...")
        if len(changes) == 0:
            print("Nothing to rebase")
            return 1
        base = None
        sequence = "noop\n"
        for local_change in reversed(changes):
            console.rule(f"Fetching: {local_change.subject}", align="left")
            can_be_base, hash = self.fetch_and_get_hash(local_change)
            if base is None and can_be_base:
                base = hash
            else:
                sequence += f"pick {hash}\n"

        if base is None:
            print("Nothing to do")
            return 1
        console.rule(f"Checkout new base: {base}", align="left")
        git["update-ref", f"-m reset: {b.local_name} to {base}", f"refs/heads/{b.local_name}", base].run_fg()
        git["reset", "--hard"].run_fg()
        git["clean", "-f", "-d"].run_fg()
        console.rule(f"Starting interactive rebase", align="left")
        with plumbum.local.env(GIT_SEQUENCE_EDITOR=f"printf '{sequence}' > "):
            git["rebase", "-i", "HEAD"].run_fg()
