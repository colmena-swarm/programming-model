#!/usr/bin/env python3
#
#  Copyright 2002-2025 Barcelona Supercomputing Center (www.bsc.es)
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
from typing import TYPE_CHECKING

from colmena.logger import Logger
from colmena.implementations.zenoh_client import ZenohClient
from colmena.implementations.pyre_client import PyreClient
from colmena.implementations import ContextAwareness

if TYPE_CHECKING:
    import colmena

def get_context_names(role):
    try:
        return role._context
    except AttributeError:
        return []

def agent_id():
    return os.getenv("AGENT_ID")

class Communications:
    """Class to handle communications using clients."""

    def __init__(self):
        self.__logger = Logger(self).get_logger()

    def start(self, role: "colmena.Role", zenoh_root: str):
        self.__pyre_client = PyreClient()
        self.__pyre_client.start()
        self.__zenoh_data_client = ZenohClient(zenoh_root)
        self.__zenoh_metrics_client = ZenohClient(f"colmena/metrics/{agent_id()}/{zenoh_root}")
        self.__zenoh_context_client = ZenohClient(f"colmena/contexts/{agent_id()}")
        self.__context_awareness = ContextAwareness(self.__zenoh_context_client, get_context_names(role))
        self.__initialize(role)

    def __initialize(self, role: "colmena.Role"):
        """Initializes channels, data, and metrics interfaces.

        Parameter:
            - role -- Role object.
        """

        try:
            for c in role.channel_info:
                channel = getattr(role, c)
                channel._set_publish_method(self.__pyre_client.publish)
                channel._set_subscribe_method(self.__pyre_client.subscribe)

        except AttributeError:
            self.__logger.debug(
                f"No channel interfaces in role '{type(role).__name__}'"
            )

        try:
            for m in role.metric_info:
                metric = getattr(role, m)
                metric._set_publish_method(lambda key, value: self.__context_awareness.context_aware_publish(key, value, self.__zenoh_metrics_client.publish))

        except AttributeError:
            self.__logger.debug(f"No metric interfaces in role '{type(role).__name__}'")

        try:
            for d in role.data_info:
                data = getattr(role, d)
                data._set_publish_method(lambda key, value, scope: self.__context_awareness.context_aware_data_set(key, value, self.__zenoh_data_client.publish, scope))
                data._set_get_method(lambda key, scope: self.__context_awareness.context_aware_data_get(key, self.__zenoh_data_client.get, scope))

        except AttributeError:
            self.__logger.debug(f"No data interfaces in role '{type(role).__name__}'")

    def stop(self):
        self.__pyre_client.stop()
