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

import os
from colmena import MetricInterface
from colmena.utils.exceptions import FunctionNotImplementedException
from colmena.utils.logger import Logger
from colmena.communications import Communications


class Role:
    """Parent class for a role defined in COLMENA."""

    def __init__(self, *args, **kwargs):
        self._running = False
        self.logger = Logger(self).get_logger()
        self._name = type(self).__name__
        try:
            self.channels = []
            for name, channel in kwargs["channels"].items():
                self.channels.append(name)
                setattr(self, name, channel)
        except KeyError:
            self.logger.debug(f"No channels in role {type(self).__name__}")

        try:
            self.data = []
            for name, data in kwargs["data"].items():
                self.data.append(name)
                setattr(self, name, data)
        except KeyError:
            self.logger.debug(f"No data in role {type(self).__name__}")

        try:
            self.metrics = []
            for name, metric in kwargs["metrics"].items():
                self.metrics.append(name)
                setattr(self, name, metric)
        except KeyError:
            self.logger.debug(f"No metrics in role {type(self).__name__}")

        self.logger.info(f"Role '{type(self).__name__}' initialized")

        _id = "num_executions"
        self.metrics.append(f"_{_id}")
        setattr(
            self,
            f"_{_id}",
            MetricInterface(f"{_id}_{self.get_hostname()}_{self._name}"),
        )

        self.comms = Communications(self)

    @property
    def kpis(self):
        try:
            return self._kpis
        except AttributeError:
            return []

    @property
    def running(self):
        return self._running

    def behavior(self):
        """
        Behavior function of a role. To be implemented in subclass.
        """
        raise FunctionNotImplementedException(func_name="behavior", class_name="Role")

    def execute(self):
        """
        Function to execute a role by running its behavior function.
        """
        self.logger.info(f"Executing role '{self._name}'")
        self._running = True
        self.behavior()

    def stop(self):
        for process in self._processes:
            process.terminate()
        self.logger.info(f"Role '{self._name}' terminated.")

    def get_hostname(self):
        try:
            _hostname = os.environ["HOSTNAME"]
        except KeyError:
            self.logger.debug("Environment variable HOSTNAME not found")
            _hostname = "localhost"
        return _hostname