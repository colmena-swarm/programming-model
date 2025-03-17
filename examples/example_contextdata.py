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
import json
import os
# -*- coding: utf-8 -*-

import time
import random
from colmena import (
    Service,
    Role,
    Requirements,
    Persistent,
    Context, Data, Metric, KPI
)

class CompanyPremises(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def locate(self, device):
        agent_id = os.getenv("AGENT_ID")
        location = {"building": agent_id}
        print(json.dumps(location))

class ExampleContextdata(Service):
    @Context(class_ref=CompanyPremises, name="company_premises")
    @Data(name="another_shared_data")
    @Data(name="shared_data", scope="company_premises/building = .")
    @Metric(name="processing_time")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Setter(Role):
        @Requirements("SENSOR")
        @Context(class_ref=CompanyPremises, name="company_premises")
        @Data(name="shared_data", scope="company_premises/building = .")
        @Metric(name="processing_time")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            shared_data = {"some_data": "some_value"}
            self.shared_data.publish(shared_data)
            self.processing_time.publish(2)
            time.sleep(5)

    class Getter(Role):
        @Requirements("GETTER")
        @Context(class_ref=CompanyPremises, name="company_premises")
        @Data(name="shared_data", scope="company_premises/building = .")
        @Data(name="another_shared_data")
        @KPI(query="avg_over_time(examplecontextdata_processing_time[5m]) < 5", scope="company_premises/building = .")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            print(self.shared_data.get())
            time.sleep(1)
