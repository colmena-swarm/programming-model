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

from colmena import (
    Service,
    Role,
    Channel,
    Data,
    Requirements,
    Metric,
    Persistent,
    Async,
)


class ExampleInterfaces(Service):
    @Channel(name="test_channel", scope=" ")
    @Data(name="test_data", scope=" ")
    @Metric(name="test_metric")
    @Data(name="evaluate", scope=" ")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Publish(Role):
        @Channel(name="test_channel")
        @Data(name="test_data")
        @Metric(name="test_metric")
        @Requirements("CAMERA")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent(period=1000)
        def behavior(self):
            self.test_data.publish(5.5)
            self.test_channel.publish("test_message")
            self.test_metric.publish(4.4)

    class Get(Role):
        @Channel(name="test_channel")
        @Data(name="test_data")
        @Data(name="evaluate")
        @Requirements("CPU")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Async(msg="test_channel")
        def behavior(self, msg):
            assert msg == "test_message"
            value = self.test_data.get()
            assert value == 5.5
            self.evaluate.publish(1)
