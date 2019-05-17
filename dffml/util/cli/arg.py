# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import copy
from typing import Optional

class Arg(dict):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(**kwargs)
        self.name = 'no-name'
        if args:
            self.name = args[0]

    def modify(self, name: Optional[str] = None, **kwargs):
        updated = copy.deepcopy(self)
        updated.update(kwargs)
        if not name is None:
            updated.name = name
        return updated
