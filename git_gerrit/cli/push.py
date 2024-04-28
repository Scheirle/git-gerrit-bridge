# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli

from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.change import Change
from git_gerrit.utils.git import git

class Push(plumbum.cli.Application):
    '''Pushes the current branch to upstream.'''
    options: list[str] = []

    skip_local_tail = plumbum.cli.Flag(("--skip-local-tail", "-s"),
        help=("Pushes the current branch to upstream, "
              "execpt all local-only changes at the end of the commit chain. "
              "Local only changes are changes that were not previously pushed to upstream."))

    @plumbum.cli.switch(("--push-option", "-o"), str,
        help="Push options forwarded to git push; e.g. -o wip -o topic=mytopic",
        list=True)
    def process_option(self, options:list[str]):
        for o in options:
            self.options.append("-o")
            self.options.append(o)

    def get_head(self, branch: LocalBranch) -> str:
        if self.skip_local_tail:
            for i, local in reversed(list(enumerate(branch.get_changes()))):
                if Change.from_local(local).remote:
                    # Last commit already known to upstream
                    return f"HEAD~{i}"
        return "HEAD" # push all

    def main(self):
        b = LocalBranch.from_head() or LocalBranch.from_rebase()
        if b is None:
            print("Current branch not known, no branch checked out?")
            return 1
        if b.remote_name == "":
            print("Current branch has no remote, cannot push to gerrit")
            return 1

        head = self.get_head(b)
        cmd = ["push", b.remote, f"{head}:refs/for/{b.remote_name}", "-o", f"hashtag=branch:{b.local_name}"] + self.options
        git[cmd].run_fg(retcode=None)
