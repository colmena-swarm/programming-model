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

from colmena import Role, Service, Dependencies, Context
from colmena.decorators.base_image import BaseImage
from colmena.exceptions import WrongClassForDecoratorException


class ServicesWithoutBaseImageDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithBaseImageDec(Role):
        @BaseImage('examplebase')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class ServiceWithBaseImageDec(Service):
    @BaseImage('examplebase')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ContextWithBaseImageDec(Context):
    @BaseImage('examplebase')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestBaseImage:

    def test_role_base_image(self):
        service = ServicesWithoutBaseImageDec()
        assert service.config['RoleWithBaseImageDec']['base_image'] == 'examplebase'

    def test_decorating_service(self):
        try:
            ServiceWithBaseImageDec()
        except WrongClassForDecoratorException:
            assert True
            return
        assert False

    def test_context_base_image(self):
        # Unsupported for now
        try:
            ContextWithBaseImageDec()
        except WrongClassForDecoratorException:
            assert True
            return
        assert False