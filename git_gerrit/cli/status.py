# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import plumbum.cli
import rich.console
import rich.table
import rich.text

from git_gerrit.utils.change import Change
from git_gerrit.utils.remotechange import RemoteChange
from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.gerrit import Gerrit

class Status(plumbum.cli.Application):
    '''Show status of remote and local changes'''

    def get_own_changes(self) -> set[Change]:
        remote_changes = Gerrit.get_remote_changes(f"owner:self is:open -is:merge")
        local_changes = LocalBranch.get_all_local_changes()
        changes = set([Change.from_remote(r) for r in remote_changes])
        changes |= set([Change.from_local(l) for l in local_changes])
        return changes

    def main(self):
        console = rich.console.Console()
        small = console.width < 110
        caption = (
            " :globe_with_meridians: Remote Change;"
            " :zap: Local Change;"
            " :beetle: WIP Change;"
            " :x: To be deleted;"
            " Click Number to open in browser")
        table = rich.table.Table(show_lines=False, caption_justify="left", caption=caption)
        table.add_column("Number", style="green", width=7)
        table.add_column("Subject", no_wrap=True, max_width=35 if small else None)
        table.add_column("Status", justify="center")
        table.add_column("Remote Branch")
        table.add_column("Local Branch", style="magenta1 bold")
        if not small:
            table.add_column("Last Update", no_wrap=True)
            table.add_column("Owner", no_wrap=True)

        def add_row(nr, subject, status, remote, local, update, owner):
            if small:
                table.add_row(nr, subject, status, remote, local)
            else:
                table.add_row(nr, subject, status, remote, local, update, owner)

        empty_remote = RemoteChange("", "","", "", [], "", "", "", datetime.datetime.now(), "", "", "", False)
        for c in sorted(self.get_own_changes(), reverse=True):
            remote = c.remote if c.remote else empty_remote
            emoji = ":globe_with_meridians:"
            if remote.wip:
                emoji = ":beetle:"
            elif remote.is_merged() or remote.is_abandoned():
                emoji = ":x:"
            elif c.remote is None:
                emoji = ":zap:"
            add_row(
                rich.text.Text(remote.number, f"link {remote.url}"),
                f"{emoji} {c.subject}",
                c.get_status(),
                c.branch_remote,
                c.local.branch_local if c.local else "",
                c.update.strftime("%Y-%m-%d %H:%M"),
                remote.owner)
        console.print(table)
