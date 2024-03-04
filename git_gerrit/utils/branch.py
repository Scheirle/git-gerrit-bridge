# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import cache
from git_gerrit.utils.localchange import LocalChange
from git_gerrit.utils.git import GitConfig, git

class LocalBranch:
    def __init__(self, ref: str):
        self.local_name = git["rev-parse", "--abbrev-ref", ref]().strip()
        self.remote_ref = git["for-each-ref", "--format=%(upstream:short)", ref]().strip()
        self.remote_name = self.remote_ref.replace(f"{GitConfig.remote()}/", "")

    def has_remote(self):
        return self.remote_ref != ""

    def get_changes(self) -> list[LocalChange]:
        if not self.has_remote():
            return []
        commit_hashes = git["log", "--first-parent", "--pretty=%H",
            f"{self.remote_ref}..{self.local_name}"]().splitlines()
        return [LocalChange.from_hash(hash, self.local_name, self.remote_name)
                for hash in commit_hashes]

    @classmethod
    def from_head(cls):
        """ Returns currently checked out branch. """
        ref = git["symbolic-ref", "-q", "HEAD"]().strip()
        return LocalBranch(ref)

    @staticmethod
    def is_head_clean():
        return git["status", "--porcelain"]() == ""

    @staticmethod
    @cache
    def get_branches():
        """ Returns all local branches. """
        refs = git["for-each-ref", "--format=%(refname)", "refs/heads/"]().splitlines()
        return [LocalBranch(ref) for ref in refs]

    @staticmethod
    @cache
    def get_all_local_changes() -> list[LocalChange]:
        commits = []
        for b in LocalBranch.get_branches():
            commits.extend(b.get_changes())
        return commits
