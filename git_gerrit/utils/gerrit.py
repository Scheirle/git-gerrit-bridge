# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import plumbum

from git_gerrit.utils.git import GitConfig
from git_gerrit.utils.remotechange import RemoteChange

class Gerrit:
    @staticmethod
    def get_remote_changes(query: str) -> list[RemoteChange]:
        remote = GitConfig.get_remote()
        gerrit = plumbum.local["ssh"][
            "-p", remote.port, remote.host,
            "gerrit", "query", "--format", "JSON", "--current-patch-set", "--"]
        reply = gerrit[f"{query}"]().splitlines()[:-1]
        return [RemoteChange.from_json(c) for c in reply]
