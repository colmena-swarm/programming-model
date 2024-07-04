#!/usr/bin/python
#
#  Copyright 2002-2024 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

import logging
import coloredlogs


class Logger:
    __slots__ = ["__logger"]

    def __init__(self, origin):
        self.__logger = logging.getLogger("colmena")
        if isinstance(origin, str):
            msg = origin
        else:
            msg = type(origin).__name__
        coloredlogs.install(
            level="DEBUG",
            logger=self.__logger,
            fmt=f"[{msg}] %(asctime)s %(levelname)s %(message)s",
        )

    def get_logger(self):
        return self.__logger
