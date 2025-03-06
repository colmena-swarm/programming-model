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

import json

from colmena.implementations.zenoh_client import ZenohClient
from colmena.logger import Logger


def decode_zenoh_value(message):
    decoded = message.decode('utf-8')
    return json.loads(decoded)["value"]

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
        new_scope = decode_zenoh_value(encoded_new_scope.payload)
        self.__logger.info(f"scope change. context: {self.context_name}, "
                           f"previousScope: {self.scope}, newScope: {new_scope}")
        self.scope = new_scope

class ContextAwareness:
    def __init__(self, context_subscriber: ZenohClient, context_names):
        self.__logger = Logger(self).get_logger()
        self.contexts = []
        # create context update subscription for each context hierarchy in the role
        for context_name in context_names:
            initial_value = context_subscriber.get(context_name)
            subscription = Context(context_name, initial_value)
            self.contexts.append(subscription)
            context_subscriber.subscribe_with_handler(context_name, subscription.handler)

    def context_aware_publish(self, key: str, value: object, publisher):
        print(f"context aware publish key: {key}, value: {value}")
        if len(self.contexts) > 0:
            for each in self.contexts:
                if each.scope is not None:
                    publisher(key + "/" + each.scope, value)
        else:
            publisher(key, value)
