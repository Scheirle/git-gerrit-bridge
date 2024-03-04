# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import json

from git_gerrit.utils.changebase import ChangeBase

@dataclasses.dataclass(frozen=True, eq=False)
class RemoteChange(ChangeBase):
    gerrit_ref: str
    hash: str
    hashtags: list[str]
    number: str
    owner: str
    status: str
    update: datetime.datetime
    subject: str
    topic: str | None
    url: str
    wip: bool

    @classmethod
    def from_json(cls, json_str: str):
        d = json.loads(json_str)
        return RemoteChange(
            branch_remote=d["branch"],
            change_id=d["id"],
            gerrit_ref=d["currentPatchSet"]["ref"],
            hash=d["currentPatchSet"]["revision"],
            hashtags=d.get("hashtags", []),
            number=str(d["number"]),
            owner=d["owner"]["name"],
            status=d["status"],
            subject=d["subject"],
            topic=d.get("topic", None),
            update=datetime.datetime.fromtimestamp(d["currentPatchSet"]["createdOn"]),
            url=d["url"],
            wip=d.get("wip", False)
        )

    def is_merged(self):
        return self.status == "MERGED"

    def is_abandoned(self):
        return self.status == "ABANDONED"

    def recommend_branch_name(self):
        hash_filter = "branch:"
        name = next(filter(lambda h: h.startswith(hash_filter), self.hashtags), None)
        if name:
            return name[len(hash_filter):]
        if self.topic:
            return self.topic
        return self.number
