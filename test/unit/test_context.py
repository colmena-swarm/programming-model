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

from colmena import Context, Service, Role


class ContextWithStructure(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structure = {"data_structure_key": "data_structure_value"}

    def locate(self, device):
        return True

class ServiceWithContext(Service):
    @Context(class_ref=ContextWithStructure, name="example_context")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithContext(Role):
        @Context(name="example_context", scope="example_scope")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class TestContext:

    def test_context_config_in_service(self):
        service = ServiceWithContext()
        assert service.context['example_context'].structure == {'data_structure_key': 'data_structure_value'}
        assert service.context['example_context'].locate(None)

    def test_context_in_role(self):
        role = ServiceWithContext.RoleWithContext(ServiceWithContext)
        assert role._context == {'example_context': 'example_scope'}