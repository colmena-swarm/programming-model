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

import json
import unittest

from colmena.implementations.context_awareness import ContextAwareness
from unittest.mock import Mock


class TestPublication:
    def __init__(self, payload):
        self.payload = payload


def to_json(value):
    return json.dumps({"value": value}, indent=4)


class TestContextAwareness(unittest.TestCase):

    def setUp(self):
        self.setter = Mock()
        self.getter = Mock()
        self.zenoh_client = Mock()
        self.zenoh_client.get_agent = Mock()
        self.zenoh_client.subscribe = Mock()
        self.zenoh_client.get_agent.return_value = (to_json('{"building": "BSC", "floor": "1", "room": "reception"}')).encode()

    def test_set_without_scope_at_top_level(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe.call_args
        subscription_handler = args[1]

        subscription_handler(TestPublication(to_json('{"building": "BSC", "floor": "2", "room": "reception"}').encode()))
        self.context_awareness.context_aware_data_set("processing_time", "1", self.setter)
        self.setter.assert_called_with("processing_time", "1")

        self.context_awareness.context_aware_data_get("processing_time", self.getter)
        self.getter.assert_called_with("processing_time")

    def test_given_scope_not_requiring_resolution_then_correctly_used(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe.call_args
        subscription_handler = args[1]

        subscription_handler(TestPublication(to_json('{"building": "BSC", "floor": "2", "room": "reception"}').encode()))
        self.context_awareness.context_aware_data_set("processing_time", "1", self.setter, "test_context/building = Repsol")
        self.setter.assert_called_with("test_context/building/Repsol/processing_time", "1")

        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building = Repsol")
        self.getter.assert_called_with("test_context/building/Repsol/processing_time")

    def test_different_scope_syntax(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe.call_args
        subscription_handler = args[1]
        subscription_handler(
            TestPublication(to_json('{"building": "BSC", "floor": "2", "room": "reception"}').encode()))
        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building = Repsol")
        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building=Repsol")
        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building= Repsol")
        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building =Repsol")

    def test_given_scope_requiring_resolution_then_correctly_resolved(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe.call_args
        subscription_handler = args[1]

        subscription_handler(TestPublication(to_json('{"building": "BSC", "floor": "2", "room": "reception"}').encode()))
        self.context_awareness.context_aware_data_set("processing_time", "1", self.setter, "test_context/building = .")
        self.setter.assert_called_with("test_context/building/BSC/processing_time", "1")

        self.context_awareness.context_aware_data_get("processing_time", self.getter, "test_context/building = .")
        self.getter.assert_called_with("test_context/building/BSC/processing_time")

