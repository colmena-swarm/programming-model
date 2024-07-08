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

from colmena.client.context_awareness import ContextAwareness
from unittest.mock import Mock


class TestPublication:
    def __init__(self, payload):
        self.payload = payload


def to_json(value):
    return json.dumps({"value": value}, indent=4)


class TestContextAwareness(unittest.TestCase):

    def setUp(self):
        self.publish = Mock()
        self.zenoh_client = Mock()
        self.zenoh_client.get = Mock()
        self.zenoh_client.subscribe = Mock()
        self.zenoh_client.get.return_value = (to_json("initial")).encode()

    def test_subscribes_to_context_updates_and_uses_scope_during_publish(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        args, _ = self.zenoh_client.subscribe_with_handler.call_args
        subscription_handler = args[1]

        subscription_handler(TestPublication(to_json("first").encode()))
        self.context_awareness.publish("context", "1", self.publish)
        self.publish.assert_called_with("context/first", "1")

        subscription_handler(TestPublication(to_json("second").encode()))
        self.context_awareness.publish("context", "2", self.publish)
        self.publish.assert_called_with("context/second", "2")
        self.assertEqual(self.publish.call_count, 2)

    def test_uses_initial_value_on_creation(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, ["test_context"])
        self.context_awareness.publish("a", "1", self.publish)
        self.publish.assert_called_with("a/initial", "1")

    def test_when_no_contexts_then_metric_published_without(self):
        self.context_awareness = ContextAwareness(self.zenoh_client, [])
        self.context_awareness.publish("a", "1", self.publish)
        self.publish.assert_called_with("a", "1")
