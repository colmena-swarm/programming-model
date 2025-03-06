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

from colmena import Role, Service, Metric
from colmena.exceptions import MetricNotExistException


class ServiceWithMetricDec(Service):
    @Metric(name='example_metric')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithMetricDec(Role):
        @Metric(name='example_metric')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class ServiceWithoutMetricDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithMetricDec(Role):
        @Metric(name='example_metric')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class TestMetric:

    def test_decorator_config_service(self):
        metrics = ServiceWithMetricDec.__init__.config['metrics']
        assert metrics == ['example_metric']

    def test_decorator_data_in_role(self):
        assert ServiceWithMetricDec().config['RoleWithMetricDec']['metrics'] == ['example_metric']

        role = ServiceWithMetricDec.RoleWithMetricDec(ServiceWithMetricDec)
        assert role.metrics[0] == 'example_metric'

        metric_interface = role.example_metric

        assert metric_interface._name == 'example_metric'


    def test_error_decorator_not_initialized(self):
        try:
            ServiceWithoutMetricDec.RoleWithMetricDec(ServiceWithoutMetricDec)
        except MetricNotExistException:
            assert True
            return
        assert False

    def test_interface(self):
        role = ServiceWithMetricDec.RoleWithMetricDec(ServiceWithMetricDec)

        zenoh_client = Mock()
        pyre_client = Mock()
        context_awareness = Mock()
        context_awareness.context_aware_publish = Mock()

        role.comms._Communications__context_awareness = context_awareness
        role.comms._Communications__pyre_client = pyre_client
        role.comms._Communications__zenoh_client = zenoh_client

        role.comms._Communications__initialize(role)

        metric_interface = role.example_metric
        metric_interface.publish(0)
        context_awareness.context_aware_publish.assert_called_once()
        args = context_awareness.context_aware_publish.call_args.args
        assert args[0] == 'example_metric'
        assert args[1] == 0
