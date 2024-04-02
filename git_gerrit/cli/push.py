# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum.cli

from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.git import GitConfig, git

class Push(plumbum.cli.Application):
    '''Pushes the current branch to upstream.'''
    options: list[str] = []

    @plumbum.cli.switch(("--push-option", "-o"), str,
        help="Push options forwarded to git push; e.g. -o wip -o topic=mytopic",
        list=True)
    def process_option(self, options:list[str]):
        for o in options:
            self.options.append("-o")
            self.options.append(o)

    def main(self):
        b = LocalBranch.from_head() or LocalBranch.from_rebase()
        if b is None:
            print("Current branch not known, no branch checked out?")
            return 1
        if b.remote_name == "":
            print("Current branch has no remote, cannot push to gerrit")
            return 1
        cmd = ["push", b.remote, f"HEAD:refs/for/{b.remote_name}", "-o", f"hashtag=branch:{b.local_name}"] + self.options
        git[cmd].run_fg(retcode=None)
