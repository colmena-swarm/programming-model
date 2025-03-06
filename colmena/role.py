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
from colmena import MetricInterface, ChannelInterface, DataInterface
from colmena.exceptions import FunctionNotImplementedException
from colmena.logger import Logger
from colmena.implementations import Communications


class Role:
    """Parent class for a role defined in COLMENA."""

    def __init__(self, *args, **kwargs):
        self._running = False
        self.logger = Logger(self).get_logger()
        self._name = type(self).__name__
        self._service_name = args[0].__name__.lower()
        try:
            self.channels = []
            for channel_name, channel_scope in kwargs["channels"].items():
                self.channels.append(channel_name)
                channel_interface = ChannelInterface(channel_name)
                channel_interface.scope = channel_scope
                setattr(self, channel_name, channel_interface)
        except KeyError:
            self.logger.debug(f"No channels in role {type(self).__name__}")

        try:
            self.data = []
            for data_name, data_scope in kwargs["data"].items():
                self.data.append(data_name)
                data_interface = DataInterface(data_name)
                data_interface.scope = data_scope
                setattr(self, data_name, data_interface)
        except KeyError:
            self.logger.debug(f"No data in role {type(self).__name__}")

        try:
            self.metrics = []
            for metric_name in kwargs["metrics"]:
                self.metrics.append(metric_name)
                metric_interface = MetricInterface(metric_name)
                setattr(self, metric_name, metric_interface)
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

        self.comms = Communications()

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

    def start(self):
        """
        Function to be executed before the role starts.
        """
        pass

    def stop(self):
        """
        Function to be executed before the role stops.
        """
        pass

    def execute(self):
        """
        Function to execute a role by running its behavior function.
        """
        self.start()
        self.comms.start(self, self._service_name)
        self.logger.info(f"Executing role '{self._name}'")
        self._running = True
        self.behavior()

    def terminate(self):
        self._running = False
        self.stop()
        try:
            for process in self._processes:
                process.join()
        except AttributeError:
            self.logger.info("Role already stopped.")
        self.comms.stop()
        self.logger.info(f"Role '{self._name}' terminated.")

    def get_hostname(self):
        try:
            _hostname = os.environ["HOSTNAME"]
        except KeyError:
            self.logger.debug("Environment variable HOSTNAME not found")
            _hostname = "localhost"
        return _hostname
