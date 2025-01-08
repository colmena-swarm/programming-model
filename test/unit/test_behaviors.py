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

from colmena import Service, Channel, Persistent, Role, Async
from busypie import wait, SECOND


class ServiceWithRoleBehaviors(Service):
    @Channel(name='example_channel', scope='*')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class PersistentRole(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.iterations = 0

        @Persistent()
        def behavior(self):
            self.example_channel.publish(self.iterations)
            self.iterations += 1
            time.sleep(0.1)

    class AsyncRole(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.iterations = 0

        @Async(message='example_channel')
        def behavior(self, message):
            print(f"message: {message}")
            self.iterations = message


class TestBehavior:

    def test_persistent(self):
        persistent_role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
        persistent_role.execute()
        wait().at_most(2, SECOND).until(lambda: persistent_role.iterations > 5)
        persistent_role.stop()

    def test_persistent_and_async(self):
        persistent_role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
        async_role = ServiceWithRoleBehaviors.AsyncRole(ServiceWithRoleBehaviors)
        async_role.execute()
        persistent_role.execute()
        wait().at_most(2, SECOND).until(lambda: async_role.iterations > 0)
        persistent_role.stop()
        async_role.stop()
