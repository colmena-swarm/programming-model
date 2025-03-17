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
import json
import os
import time
import zenoh
from zenoh import Config

from colmena.logger import Logger

def agent_id():
    return os.getenv("AGENT_ID")
 
class ZenohClient:
    def __init__(self, root: str):
        self._logger = Logger(self).get_logger()
        self._logger.info(f"Starting Zenoh client. agentId: {agent_id()}")
        self._publishers = {}
        self._subscribers = {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        zenoh_config_path = os.path.join(script_dir, 'zenoh_config.json5')
        self._session = zenoh.open(zenoh.Config.from_file(zenoh_config_path))
        self._root = root

    def publish(self, key: str, value: object):
        composite_key = f"{self._root}/{key}"
        try:
            self._publishers[key].put(payload=value, encoding="application/json")
            self._logger.debug(f"published. key: '{composite_key}', value: '{json.dumps(value)}'")
        except KeyError:
            self._publishers[key] = self._session.declare_publisher(key_expr=f"{composite_key}", encoding="application/json")
            self._logger.debug(f"new publisher. key: '{composite_key}'")
            self.publish(key, value)

    def subscribe(self, key: str, handler):
        composite_key = f"{self._root}/{key}"
        subscription = self._session.declare_subscriber(f"{composite_key}", handler)
        self._subscribers[key] = subscription
        self._logger.debug(f"new handler subscription. key: '{composite_key}'")

    def put(self, key: str, value: bytes):
        composite_key = f"{self._root}/{key}/{agent_id()}"
        self._session.put(f"{composite_key}", payload=value, encoding="application/json")
        self._logger.debug(f"new data value stored: '{composite_key}'")

    def get_agent(self, key: str) -> object:
        composite_key = f"{self._root}/{key}"
        return self._get(composite_key)

    def get(self, key: str) -> object:
        composite_key = f"{self._root}/{key}"
        return self._get(composite_key)

    def _get(self, key: str):
        while True:
            replies = self._session.get(f"{key}")
            for reply in replies:
                try:
                    message_payload = reply.ok.payload.to_string()
                    self._logger.debug(f"new value retrieved. key: {key}, value: {message_payload}")
                    return message_payload
                except:
                    self._logger.debug("Received (ERROR: '{}')")
            wait_time = 5
            self._logger.info(f"Key not present, waiting {wait_time} seconds. Key: {key}")
            time.sleep(wait_time)
