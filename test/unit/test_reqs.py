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

from colmena import Role, Service, Requirements
from colmena.exceptions import WrongClassForDecoratorException


class ServicesWithoutRequirementsDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithRequirementsDec(Role):
        @Requirements('example_reqs')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class ServiceWithRequirementsDec(Service):
    @Requirements('example_reqs')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestRequirements:

    def test_role_reqs(self):
        service = ServicesWithoutRequirementsDec()
        assert service.config['RoleWithRequirementsDec']['reqs'] == ['example_reqs']

    def test_decorating_service(self):
        try:
            ServiceWithRequirementsDec()
        except WrongClassForDecoratorException:
            assert True
            return
        assert False