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

from colmena import Role, Service, Version, Context
from colmena.exceptions import WrongClassForDecoratorException


class ServicesWithoutVersionDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithVersionDec(Role):
        @Version('0.0.0')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class ServiceWithVersionDec(Service):
    @Version('0.0.0')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ContextWithVersionDec(Context):
    @Version('0.0.0')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestVersion:

    def test_role_version(self):
        service = ServicesWithoutVersionDec()
        assert service.config['RoleWithVersionDec']['version'] == '0.0.0'

    def test_decorating_service(self):
        try:
            ServiceWithVersionDec()
        except WrongClassForDecoratorException:
            assert True
            return
        assert False

    def test_context_version(self):
        context = ContextWithVersionDec()
        assert context.version == '0.0.0'