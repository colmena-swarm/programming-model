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

from colmena import Service, Role


class ServiceWithoutDecorators(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithoutDecorators(Role):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def behavior(self):
            pass

        def start(self):
            self._started = True

        def stop(self):
            self._stoped = True

class TestRole:

    def test_no_decs(self):
        role = ServiceWithoutDecorators.RoleWithoutDecorators(ServiceWithoutDecorators)
        role.execute()
        role.terminate()

    def test_start_and_stop(self):
        role = ServiceWithoutDecorators.RoleWithoutDecorators(ServiceWithoutDecorators)
        role.execute()
        role.terminate()

        assert role._started
        assert role._stoped

