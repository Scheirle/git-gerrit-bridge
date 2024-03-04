# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime

from git_gerrit.utils.git import git
from git_gerrit.utils.changebase import ChangeBase

@dataclasses.dataclass(frozen=True, eq=False)
class LocalChange(ChangeBase):
    branch_local: str
    hash: str
    update: datetime.datetime
    subject: str

    @classmethod
    def _get_commit_info(cls, hash: str) -> tuple[str, str, datetime.datetime]:
        """ Returns the commit message, the change id and the timestamp of the commit. """
        change_id_prefix = "Change-Id: "
        out = git["log", "--format=%ct%n%B", "-n", 1, hash]().splitlines()
        change_ids = [x for x in out if x.startswith(change_id_prefix)]
        assert len(change_ids) != 0, f"Change {hash} has no change id"
        date = datetime.datetime.fromtimestamp(int(out[0]))
        subject = out[1]
        change_id = change_ids[-1][len(change_id_prefix):]
        return (subject, change_id, date)

    @classmethod
    def from_hash(cls, hash: str, branch_local:str, branch_remote:str):
        subject, change_id, date = cls._get_commit_info(hash)
        return cls(
            branch_local=branch_local,
            branch_remote=branch_remote,
            change_id=change_id,
            hash=hash,
            subject=subject,
            update=date,
        )
