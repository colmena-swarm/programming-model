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
import threading
from time import sleep

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

        @Persistent(period=1)
        def behavior(self):
            self.example_channel.publish(self.iterations)
            self.iterations += 1
            print("One more iteration")

    class AsyncRole(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.iterations = 0

        @Async(message='example_channel')
        def behavior(self, message):
            print(f"message: {message}")
            self.logger.info("Executing async")
            self.iterations = message


class TestBehavior:

    def test_persistent(self):
        def start_persistent():
            role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
            self.role = role
            role.execute(test=True)

        thread = threading.Thread(target=start_persistent)
        thread.start()

        wait().at_most(5, SECOND).until(
            lambda: any(thread.is_alive() for thread in threading.enumerate() if isinstance(thread, threading.Thread))
        )
        self.role.terminate()

    def test_persistent_and_async(self):
        def start_persistent():
            role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
            self.persistent_role = role
            role.execute(test=True)

        def start_async():
            role = ServiceWithRoleBehaviors.AsyncRole(ServiceWithRoleBehaviors)
            self.async_role = role
            role.execute(test=True)

        # Launch both threads
        persistent_thread = threading.Thread(target=start_persistent)
        async_thread = threading.Thread(target=start_async)

        persistent_thread.start()
        sleep(1)
        async_thread.start()

        wait().at_most(5, SECOND).until(lambda: hasattr(self, 'async_role') and self.async_role.iterations > 0)

        # Stop the roles
        self.persistent_role.terminate()
        self.async_role.terminate()

        persistent_thread.join()
        async_thread.join()


