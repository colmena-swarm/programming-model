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

from unittest.mock import Mock

from colmena import Role, Service
from colmena.data import Data
from colmena.exceptions import DataNotExistException


class ServiceWithDataDec(Service):
    @Data(name='example_data', scope='*')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithDataDec(Role):
        @Data(name='example_data')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class ServiceWithoutDataDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithDataDec(Role):
        @Data(name='example_data')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class TestData:

    def test_decorator_config_service(self):
        data = ServiceWithDataDec.__init__.config['data']
        assert data == {'example_data': '*'}

    def test_decorator_data_in_role(self):
        assert ServiceWithDataDec().config['RoleWithDataDec']['data'] == ['example_data']

        role = ServiceWithDataDec.RoleWithDataDec(ServiceWithDataDec)
        assert role.data[0] == 'example_data'

        data_interface = role.example_data

        assert data_interface._name == 'example_data'
        assert data_interface._scope == '*'

    def test_error_decorator_not_initialized(self):
        try:
            ServiceWithoutDataDec.RoleWithDataDec(ServiceWithoutDataDec)
        except DataNotExistException:
            assert True
            return
        assert False

    def test_interface(self):
        role = ServiceWithDataDec.RoleWithDataDec(ServiceWithDataDec)

        zenoh_client = Mock()
        pyre_client = Mock()
        context_awareness = Mock()

        role.comms._Communications__context_awareness = context_awareness
        role.comms._Communications__pyre_client = pyre_client
        role.comms._Communications__zenoh_client = zenoh_client

        role.comms._Communications__initialize(role)

        data_interface = role.example_data
        data_interface.publish(0)
        kwargs = context_awareness.publish.call_args.kwargs
        assert kwargs['key'] == 'example_data'
        assert kwargs['value'] == 0

        data_interface.get()
        kwargs = zenoh_client.get.call_args.kwargs
        assert kwargs['key'] == 'example_data'
