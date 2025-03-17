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

# fails when context awareness old_sla = True
class TestContextAwareness(unittest.TestCase):

    def setUp(self):
        self.publish = Mock()
        self.zenoh_client = Mock()
        self.zenoh_client.get_agent = Mock()
        self.zenoh_client.subscribe = Mock()
        self.zenoh_client.get_agent.return_value = '{"building": "BSC", "floor": "1", "room": "reception"}'

    def test_subscribes_to_context_updates_and_uses_scope_during_publish(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe.call_args
        subscription_handler = args[1]

        subscription_handler(TestPublication('{"building": "BSC", "floor": "2", "room": "reception"}'))
        self.context_awareness.context_aware_publish("processing_time", "1", self.publish)
        self.publish.assert_called_with("processing_time", '{"test_context/building": "BSC", "test_context/floor": "2", "test_context/room": "reception", "value": "1"}')

        subscription_handler(TestPublication('{"building": "BSC", "floor": "2", "room": "reception"}'))
        self.context_awareness.context_aware_publish("processing_time", "2", self.publish)
        self.publish.assert_called_with("processing_time", '{"test_context/building": "BSC", "test_context/floor": "2", "test_context/room": "reception", "value": "2"}')
        self.assertEqual(self.publish.call_count, 2)

    def test_uses_initial_value_on_creation(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        self.context_awareness.context_aware_publish("a", "1", self.publish)
        self.publish.assert_called_with("a", '{"test_context/building": "BSC", "test_context/floor": "1", "test_context/room": "reception", "value": "1"}')

    def test_when_no_contexts_then_metric_published_without(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, [])
        self.context_awareness.context_aware_publish("a", "1", self.publish)
        self.publish.assert_called_with("a", '{"value": "1"}')
