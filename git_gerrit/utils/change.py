# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import rich.text

from functools import cached_property, total_ordering
from git_gerrit.utils.branch import LocalBranch
from git_gerrit.utils.changebase import ChangeBase
from git_gerrit.utils.gerrit import Gerrit
from git_gerrit.utils.localchange import LocalChange
from git_gerrit.utils.remotechange import RemoteChange

@total_ordering
@dataclasses.dataclass(frozen=True)
class Change(ChangeBase):
    _root: LocalChange | RemoteChange

    @classmethod
    def from_remote(cls, remote: RemoteChange):
        return cls( remote.branch_remote, remote.change_id, remote)

    @classmethod
    def from_local(cls, local: LocalChange):
        return cls(local.branch_remote, local.change_id, local)

    @cached_property
    def local(self) -> LocalChange | None:
        if isinstance(self._root, LocalChange):
            return self._root

        for c in LocalBranch.get_all_local_changes():
            if Change.from_local(c) == Change.from_remote(self._root):
                return c
        return None

    @cached_property
    def remote(self) -> RemoteChange | None:
        if isinstance(self._root, RemoteChange):
            return self._root

        changes = Gerrit.get_remote_changes(
            f"change:{self._root.change_id} branch:{self._root.branch_remote} limit:1")
        assert len(changes) <= 1
        if len(changes) == 0:
            return None
        return changes[0]

    @property
    def subject(self):
        return self._root.subject

    @property
    def update(self):
        if self.local is None or self.remote is None:
            return self._root.update
        return self.local.update if self.local.update > self.remote.update else self.remote.update

    def __eq__(self, rhs):
        return hash(self) == hash(rhs)

    def __hash__(self):
        return hash((self.branch_remote, self.change_id))

    def __lt__(self, rhs):
        def wip(obj) -> bool:
            return obj.remote.wip if obj.remote else False
        def abandoned(obj) -> bool:
            return obj.remote.is_abandoned() if obj.remote else False
        def merged(obj) -> bool:
            return obj.remote.is_merged() if obj.remote else False
        return (not abandoned(self), not merged(self), not wip(self), bool(self.remote), self.update) < \
               (not abandoned(rhs),  not merged(rhs),  not wip(rhs),  bool(rhs.remote),  rhs.update)

    def get_status(self):
        if not self.local:
            return rich.text.Text("Only Remote", style="turquoise2")
        if not self.remote:
            return rich.text.Text("Only Local", style="dark_turquoise")
        if self.remote.is_merged():
            return rich.text.Text("Merged", style="purple")
        if self.remote.is_abandoned():
            return rich.text.Text("Abandoned", style="red")
        if self.local.hash == self.remote.hash:
            return rich.text.Text("In Sync", style="green")
        if self.local.update and self.remote.update:
            if self.local.update < self.remote.update:
                return rich.text.Text("Old Local", style="red")
            return rich.text.Text("Old Remote", style="yellow")
        return ""
