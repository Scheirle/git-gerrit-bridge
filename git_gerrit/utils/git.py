# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
import datetime
import plumbum
import re

from functools import cache

git = plumbum.local["git"]

@dataclasses.dataclass(frozen=True)
class Remote:
    regex = re.compile(r"ssh://.*?@(.*?):(.*?)/.*")
    name: str
    host: str
    port: str

    @staticmethod
    def create(name:str):
        rc, stdout, _ = git["remote", "get-url", "--push", name].run(retcode=None)
        match = Remote.regex.match(stdout.strip())
        if not match:
            return None
        host, port = match.groups()
        return Remote(name, host, port)

class GitConfig:
    @staticmethod
    def repo_in_current_working_directory() -> bool:
        rc, stdout, _ = git["rev-parse", "--is-inside-work-tree"].run(retcode=None)
        return rc == 0 and stdout.strip() == "true"

    @staticmethod
    @cache
    def get_remote() -> Remote:
        remotes = git["remote"]().splitlines()
        for name in remotes:
            remote = Remote.create(name)
            if remote:
                return remote
        assert False, "No git ssh remote found."

    @staticmethod
    def remote() -> str:
        return GitConfig.get_remote().name
