# Git Gerrit Bridge

[![PyPI - Version](https://img.shields.io/pypi/v/git-gerrit-bridge.svg)](https://pypi.org/project/git-gerrit-bridge)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/git-gerrit-bridge.svg)](https://pypi.org/project/git-gerrit-bridge)

-----

**Table of Contents**

- [Motivation](#motivation)
- [Usage](#usage)
- [Installation](#installation)
- [License](#license)

## Motivation
Working with git and gerrit can be done in numerous ways, just to name a few:
* No local branches and purely in detached HEAD mode
* One local branch per remote branch
* One local branch per bug/feature

Feature branches have the downside that there will be many and to keep the overview
they have to be cleaned up/deleted regularly.

Git can do this for fully integrated branches with `git branch -d <branch>`.
The issue is that often changes are purely modified in gerrit (rebase or online edits),
preventing git from detecting if a local branch is fully integrated or not (git hashes differ).

The `git gerrit` script maps local changes to remote changes and can therefore handle such situations.<br>
Let's look at an example usage.

## Usage
* Create a new local branch `topic-1`, tracking the remote `origin/development` branch:<br>
  `git gerrit new development topic-1`
* Do the implementation and commit:<br>
  `touch feature.txt`<br>
  `git add feature.txt`<br>
  `git commit -m "Added feature.txt"`
* Upload changes to gerrit (Commit chains are fine):<br>
  The remote tracking branch is automatically used as target<br>
  `git gerrit push`
* Get an overview of your changes (remote and local):<br>
  `git gerrit status`<br>
```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Number  ┃ Subject                                       ┃   Status    ┃ Remote Branch  ┃ Local Branch ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 1000001 │ 🌐 Change only available in gerrit            │ Only Remote │ development    │              │
│ 1000003 │ 🌐 Change was edited or rebased in gerrit     │  Old Local  │ development    │ stale        │
│ 1000004 │ 🌐 Change was amended locally                 │ Old Remote  │ development    │ active       │
│ 1000009 │ 🌐 Added feature.txt                          │   In Sync   │ development    │ topic-1      │
│ 1000005 │ 🌐 Local and remote change have the same hash │   In Sync   │ feature-1      │ chain        │
│         │ ⚡ Local change not yet pushed to gerrit      │ Only Local  │ hot-fix        │ hacking      │
│ 1000006 │ 🐞 Follow up for 1000005 as commit chain      │   In Sync   │ feature-1      │ chain        │
│ 1000007 │ ❌ Change was merged in gerrit                │   Merged    │ development    │ bug123       │
│ 1000008 │ ❌ Change was abandoned in gerrit             │  Abandoned  │ development    │ bug321       │
└─────────┴───────────────────────────────────────────────┴─────────────┴────────────────┴──────────────┘
 🌐 Remote Change; ⚡ Local Change; 🐞 WIP Change; ❌ To be deleted; Click Number to open in browser
```

* Remove fully integrated branches:<br>
  `git gerrit clean`<br>
```
Cleaning 8 branches:
branch_with_no_remote  ? Commits Skipped (no remote set)
active                 1 Commits Skipped (Not yet merged)
bug123                 1 Commits Deleted
bug321                 1 Commits Deleted
chain                  2 Commits Skipped (Not yet merged)
hacking                1 Commits Skipped (Not yet pushed)
stale                  1 Commits Skipped (Not yet merged)
topic-1                1 Commits Skipped (Not yet merged)
```

Further commands are:
* `git gerrit checkout <number> <branch>`<br>
  to download and checkout a gerrit change in a new local branch
* `git gerrit rebase`<br>
  to start an interactive rebase of the local changes without rebasing on the remote.
* `git gerrit sync`<br>
  to rebase the current branch by picking remote and local changes depending on which is newer.

## Installation

```console
pip install git-gerrit-bridge
```

## License

`git-gerrit` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
