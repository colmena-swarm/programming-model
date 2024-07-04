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
from typing import TYPE_CHECKING
import grpc
from colmena.grpc import route_guide_pb2_grpc
from colmena.grpc.colmena_grpc_client import ColmenaClient
from colmena.utils.logger import Logger

if TYPE_CHECKING:
    import colmena


class Communications:
    """Class to handle communications with GRPC."""

    def __init__(self, role: "colmena.Role"):
        self.__logger = Logger(self).get_logger()
        try:
            self.__ip = os.environ["DCP_IP_ADDRESS"]
        except KeyError:
            self.__logger.debug(
                "Environment variable DCP_IP_ADDRESS not set. Setting it to 'localhost'"
            )
            self.__ip = "localhost"
        self.__logger.debug(f"DCP_IP_ADDRESS: {self.__ip}")

        c = grpc.insecure_channel(f"{self.__ip}:5555")
        stub = route_guide_pb2_grpc.ColmenaPlatformStub(c)
        self.__client = ColmenaClient(stub)
        self.__initialize_grpc(role)

    def __initialize_grpc(self, role: "colmena.Role"):
        """Initializes channels, data, and metrics interfaces.

        Parameter:
            - role -- Role object.
        """
        try:
            for c in role.channels:
                channel = getattr(role, c)
                channel._set_publish_method(self.__client.publish_message)
                channel._set_subscribe_method(self.__client.subscribe)

        except AttributeError:
            self.__logger.debug(
                f"No channel interfaces in role '{type(role).__name__}'"
            )

        try:
            for m in role.metrics:
                metric = getattr(role, m)
                metric._set_publish_method(self.__client.publish_metric)
        except AttributeError:
            self.__logger.debug(f"No metric interfaces in role '{type(role).__name__}'")

        try:
            for d in role.data:
                data = getattr(role, d)
                data._set_publish_method(self.__client.publish_data)
                data._set_get_method(self.__client.get_data)

        except AttributeError:
            self.__logger.debug(f"No data interfaces in role '{type(role).__name__}'")
