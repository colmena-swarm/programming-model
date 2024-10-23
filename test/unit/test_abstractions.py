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

from colmena import Role, Service, Channel, Metric
from colmena.data import Data

class ServiceWithThreeDecorators(Service):
    @Data(name='example_data', scope='*')
    @Channel(name='example_channel', scope='*')
    @Metric(name='example_metric')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithThreeDecorators(Role):
        @Data(name='example_data')
        @Channel(name='example_channel')
        @Metric(name='example_metric')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class TestAbstractions:

    def test_decorator_config_service(self):
        data = ServiceWithThreeDecorators.__init__.config['data']
        assert data == {'example_data': '*'}

        channel = ServiceWithThreeDecorators.__init__.config['channels']
        assert channel == {'example_channel': '*'}

        metrics = ServiceWithThreeDecorators.__init__.config['metrics']
        assert metrics == ['example_metric']


    def test_decorator_data_in_role(self):
        role = ServiceWithThreeDecorators.RoleWithThreeDecorators(ServiceWithThreeDecorators)
        assert role.data[0] == 'example_data'
        data_interface = role.example_data

        assert data_interface._name == 'example_data'
        assert data_interface._scope == '*'

        assert role.channels[0] == 'example_channel'
        channel_interface = role.example_channel

        assert channel_interface._name == 'example_channel'
        assert channel_interface._scope == '*'

        assert role.metrics[0] == 'example_metric'
        metric_interface = role.example_metric

        assert metric_interface._name == 'example_metric'



