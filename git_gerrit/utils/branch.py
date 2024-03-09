# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

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
        changes = [LocalChange.from_hash(hash, self.local_name, self.remote_name)
                   for hash in commit_hashes]
        return [c for c in changes if c is not None]

    @classmethod
    def from_head(cls):
        """ Returns currently checked out branch. """
        rc, ref, _ = git["symbolic-ref", "-q", "HEAD"].run(retcode=None)
        return LocalBranch(ref.strip()) if rc == 0 else None

    @classmethod
    def from_rebase(cls):
        """ Returns the branch currently being rebased. """
        for dir in ["rebase-merge", "rebase-apply"]:
            path = git["rev-parse", "--git-path", f"{dir}/head-name"]().strip()
            if pathlib.Path(path).exists():
                ref = pathlib.Path(path).read_text().strip()
                return LocalBranch(ref)
        return None

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
