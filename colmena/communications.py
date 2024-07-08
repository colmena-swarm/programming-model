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

from typing import TYPE_CHECKING

from colmena.utils.logger import Logger
from colmena.client import ZenohClient, PyreClient

if TYPE_CHECKING:
    import colmena


class Communications:
    """Class to handle communications using clients."""

    def __init__(self, role: "colmena.Role", zenoh_root: str):
        self.__logger = Logger(self).get_logger()
        self.__pyre_client = PyreClient()
        self.__pyre_client.start()
        self.__zenoh_client = ZenohClient(zenoh_root)
        self.__initialize(role)

    def __initialize(self, role: "colmena.Role"):
        """Initializes channels, data, and metrics interfaces.

        Parameter:
            - role -- Role object.
        """
        try:
            for c in role.channels:
                channel = getattr(role, c)
                channel._set_publish_method(self.__pyre_client.publish)
                channel._set_subscribe_method(self.__pyre_client.subscribe)

        except AttributeError:
            self.__logger.debug(
                f"No channel interfaces in role '{type(role).__name__}'"
            )

        try:
            for m in role.metrics:
                metric = getattr(role, m)
                metric._set_publish_method(self.__zenoh_client.publish)
        except AttributeError:
            self.__logger.debug(f"No metric interfaces in role '{type(role).__name__}'")

        try:
            for d in role.data:
                data = getattr(role, d)
                data._set_publish_method(self.__zenoh_client.put)
                data._set_get_method(self.__zenoh_client.get)

        except AttributeError:
            self.__logger.debug(f"No data interfaces in role '{type(role).__name__}'")
