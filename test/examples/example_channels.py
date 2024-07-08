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

import time
from colmena import (
    Service,
    Role,
    Persistent,
    Channel,
    Async,
)


class ExampleChannels(Service):
    @Channel(name="test_channel", scope=" ")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Publisher(Role):
        @Channel(name="test_channel")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.i = 0

        @Persistent()
        def behavior(self):
            self.test_channel.publish(str(self.i))
            print(f"publishing {self.i}")
            self.i += 1
            time.sleep(1)

    class Receiver(Role):
        @Channel(name="test_channel")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Async(msg="test_channel")
        def behavior(self, msg):
            print(f"received {msg}")
