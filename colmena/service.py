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

from typing import List
from colmena.utils.logger import Logger


class Service:
    """Parent class for services defined in COLMENA."""

    def __init__(self):
        self.logger = Logger(self).get_logger()
        self._roles = {}

        self.config = self.get_info()
        if not hasattr(self, "data"):
            self.__data = {}
        if not hasattr(self, "channels"):
            self.__channels = {}
        if not hasattr(self, "metrics"):
            self.__metrics = {}

    @property
    def kpis(self):
        try:
            return self._kpis
        except AttributeError:
            return []

    @property
    def context(self):
        try:
            return self._context
        except AttributeError:
            self.logger.debug(f"No custom Context defined for {type(self).__name__}")

    def get_role_names(self) -> List[str]:
        return list(self._roles.keys())

    def get_info(self):
        """
        Get all information from decorators in the Service and Role classes.
        :return: Dict with configuration
        """
        config = {"kpis": self.kpis}
        for role_name in list(type(self).__dict__.keys())[2:-1]:
            role = getattr(self, role_name)
            self._roles[role_name] = role.__init__.config
        return config | self._roles