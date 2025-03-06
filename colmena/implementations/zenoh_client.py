#!/usr/bin/python
#
#  Copyright 2002-2023 Barcelona Supercomputing Center (www.bsc.es)
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

import time

# -*- coding: utf-8 -*-

from zenoh import Reliability
import zenoh
from colmena.logger import Logger


class ZenohClient:
    def __init__(self, root: str):
        self._logger = Logger(self).get_logger()
        self._publishers = {}
        self._subscribers = {}
        self._session = None
        self._root = root

    @property
    def __session(self):
        if self._session is None:
            self._session = zenoh.open()
        return self._session

    @__session.setter
    def __session(self, s):
        self._session = s

    def publish(self, key: str, value: object):
        try:
            self._publishers[key].put(value)
            self._logger.debug(f"Published key: '{self._root}/{key}', value: '{value}'")
        except KeyError:
            self._publishers[key] = self.__session.declare_publisher(
                f"{self._root}/{key}"
            )
            self._logger.debug(f"New publisher. key: '{self._root}/{key}'")
            self.publish(key, value)
        self.__session.close()

    def subscribe(self, key: str):
        try:
            return self._subscribers[key]
        except KeyError:
            self._subscribers[key] = self.__session.declare_subscriber(
                f"{self._root}/{key}", zenoh.Queue(), reliability=Reliability.RELIABLE()
            )
            return self._subscribers[key]

    def subscribe_with_handler(self, key: str, handler):
        subscription = self.__session.declare_subscriber(f"{self._root}/{key}", handler)
        self._subscribers[key] = subscription
        self._logger.debug(f"New subscription. key: '{self._root}/{key}'")

    def put(self, key: str, value: bytes):
        self.__session.put(f"{self._root}/{key}", value)
        self._logger.debug(f"New data value stored: '{key}'")
        self.__session.close()

    def get(self, key: str) -> object:
        while True:
            replies = self.__session.get(f"{self._root}/{key}", zenoh.ListCollector())
            try:
                reply = replies()[0].ok.payload
                self.__session.close()
                return reply
            except IndexError:
                self._logger.debug(f"could not get from zenoh. key: {key}")
                time.sleep(1)
