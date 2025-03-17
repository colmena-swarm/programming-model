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

from colmena import Role, Service, KPI

class ServiceWithoutKPIDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithKPIDec(Role):
        @KPI('example_kpi_expression')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class ServiceWithKPIDec(Service):
    @KPI('example_kpi_expression')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestKPI:

    def test_role_kpi(self):
        role = ServiceWithoutKPIDec.RoleWithKPIDec(ServiceWithoutKPIDec)
        assert role.kpis[0] == 'example_kpi_expression'

        assert ServiceWithoutKPIDec().config['RoleWithKPIDec']['kpis'] == [{'query': 'example_kpi_expression'}]

    def test_service_kpi(self):
        service = ServiceWithKPIDec()
        assert service.kpis[0] == 'example_kpi_expression'
        assert service.config['kpis'] == ['example_kpi_expression']