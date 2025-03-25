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
import os
import time
import zenoh
from colmena.logger import Logger

def agent_id():
    return os.getenv("AGENT_ID")
 
class ZenohClient:
    def __init__(self, root: str):
        self._logger = Logger(self).get_logger()
        self._publishers = {}
        self._subscribers = {}
        self._session = zenoh.open()
        self._root = root

    def publish(self, key: str, value: object):
        composite_key = f"{self._root}/{key}/{agent_id()}"
        try:
            self._publishers[key].put(value)
            self._logger.debug(f"published. key: '{composite_key}', value: '{value}'")
        except KeyError:
            self._publishers[key] = self._session.declare_publisher(f"{composite_key}")
            self._logger.debug(f"new publisher. key: '{composite_key}'")
            self.publish(key, value)

    def subscribe(self, key: str, handler):
        composite_key = f"{self._root}/{key}/{agent_id()}"
        subscription = self._session.declare_subscriber(f"{composite_key}", handler)
        self._subscribers[key] = subscription
        self._logger.debug(f"new handler subscription. key: '{composite_key}'")

    def put(self, key: str, value: bytes):
        composite_key = f"{self._root}/{key}/{agent_id()}"
        self._session.put(f"{composite_key}", value)
        self._logger.debug(f"new data value stored: '{composite_key}'")

    def get_agent(self, key: str) -> object:
        composite_key = f"{self._root}/{key}/{agent_id()}"
        return self._get(composite_key)

    def get(self, key: str) -> object:
        composite_key = f"{self._root}/{key}/*"
        return self._get(composite_key)

    def _get(self, key: str):
        while True:
            replies = self._session.get(f"{key}", zenoh.ListCollector())
            try:
                reply = max(replies(), key=lambda e: e.ok.timestamp)
                message_payload = reply.ok.payload
                self._logger.debug(f"new value retrieved. key: {key}, value: {message_payload}")
                return message_payload
            except (IndexError, ValueError):
                self._logger.debug(f"could not get from zenoh. key: {key}")
                time.sleep(1)
