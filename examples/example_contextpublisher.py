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

import time
import random
from colmena import (
    Service,
    Role,
    Requirements,
    Metric,
    Persistent,
    KPI, Context,
)

class CompanyPremises(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structure = {
            "floor1": ["reception"],
            "floor2": ["reception", "open_space"],
            "floor3": ["open_space", "manager_office"],
        }

    def locate(self, device):
        print("test_context")

class ExampleContextpublisher(Service):

    @Metric(name="moisture")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Publisher(Role):
        @Metric(name="moisture")
        @Context(class_ref=CompanyPremises, name="company_premises")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            self.moisture.publish(15)
            time.sleep(1)

