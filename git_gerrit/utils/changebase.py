# SPDX-FileCopyrightText: 2024-present Bernhard Scheirle
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses

@dataclasses.dataclass(frozen=True)
class ChangeBase:
    branch_remote: str
    change_id: str
