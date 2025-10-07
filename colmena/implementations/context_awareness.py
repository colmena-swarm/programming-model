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

import json
import re

from colmena.implementations.zenoh_client import ZenohClient
from colmena.logger import Logger

pattern = r"^([\w-]+)/([\w-]+)\s*=\s*(.+)$"

def decode_zenoh_value(message):
    return message

def get_context_names(role):
    try:
        return role._context
    except AttributeError:
        return []


class Context:
    def __init__(self, context_name, initial_value):
        self.__logger = Logger(self).get_logger()
        self.context_name = context_name
        decoded_initial_value = decode_zenoh_value(initial_value)
        self.__logger.info(f"scope initialised. context: {self.context_name}, "
                           f"value: {decoded_initial_value}")
        self.scope = decoded_initial_value

    def handler(self, encoded_new_scope):
        new_scope = decode_zenoh_value(encoded_new_scope.payload.to_string())
        self.__logger.info(f"scope change. context: {self.context_name}, "
                           f"previousScope: {self.scope}, newScope: {new_scope}")
        self.scope = new_scope

class ContextAwareness:
    def __init__(self, context_subscriber: ZenohClient, context_names):
        self.__logger = Logger(self).get_logger()
        self.contexts = {}

        # Get initial value for each context and then subscribe for updates
        for context_name in context_names:
            initial_value = context_subscriber.get_agent(context_name)
            subscription = Context(context_name, initial_value)
            self.contexts[context_name] = subscription
            context_subscriber.subscribe(context_name, subscription.handler)

    def context_aware_publish(self, key: str, value: object, publisher):
        metric_payload = {}
        for _, each in self.contexts.items():
            for scope_key, scope_value in json.loads(each.scope).items():
                metric_payload[each.context_name + "/" + scope_key] = scope_value
        metric_payload["value"] = value
        publisher(key, json.dumps(metric_payload))

    def context_aware_data_get(self, key: str, getter, scope: str = None):
        if scope is None:
            return getter(key)

        match = re.match(pattern, scope)
        if match:
            context_name = match.group(1)
            scope_key = match.group(2)
            scope_value = match.group(3)

            if "." in scope_value:
                try:
                    context = self.contexts[context_name]
                    scope_value = json.loads(context.scope)[scope_key]
                    return getter(f"{context_name}/{scope_key}/{scope_value}/{key}")
                except KeyError:
                    self.__logger.info(f"context_name {context_name} not set")
                    return {}
            else:
                return getter(f"{context_name}/{scope_key}/{scope_value}/{key}")
        else:
            raise ValueError(f"scope {scope} has invalid format")

    def context_aware_data_set(self, key: str, value: object, setter, scope: str = None):
        if not scope:
            setter(key, value)
            return

        match = re.match(pattern, scope)
        if match:
            context_name = match.group(1)
            scope_key = match.group(2)
            scope_value = match.group(3)

            if "." in scope_value:
                try:
                    context = self.contexts[context_name]
                    scope_value = json.loads(context.scope)[scope_key]
                    self.__logger.info(f"data key {context_name}/{scope_key}/{scope_value}/{key}, value {value}")
                    setter(f"{context_name}/{scope_key}/{scope_value}/{key}", json.dumps(value))
                except {KeyError, AttributeError}:
                    self.__logger.info(f"context_name {context_name} not set")
                    return
            else:
                setter(f"{context_name}/{scope_key}/{scope_value}/{key}", json.dumps(value))
        else:
            raise ValueError(f"scope {scope} has invalid format")
