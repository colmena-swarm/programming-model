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
import numpy as np
from datetime import datetime
from colmena import (
    Context,
    Service,
    Role,
    Channel,
    Requirements,
    Metric,
    Persistent,
    Async,
    KPI, Dependencies,
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
        current_seconds = datetime.now().second
        if current_seconds <= 12:
            print("floor1/reception")
        elif current_seconds > 12 and current_seconds <= 24:
            print("floor2/reception")
        elif current_seconds > 24 and current_seconds <= 36:
            print("floor2/open_space")
        elif current_seconds > 36 and current_seconds <= 48:
            print("floor3/open_space")
        else:
            print("floor3/manager_office")


class ExampleApplication(Service):
    @Context(class_ref=CompanyPremises, name="company_premises")
    @Channel(name="buffer", scope=" ")
    @Channel(name="result", scope=" ")
    @Metric(name="sensed")
    @Metric(name="processed")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Sensing(Role):
        @Context(name="company_premises", scope="*.*.lobby")
        @Channel(name="buffer")
        @Metric(name="sensed")
        @Requirements("CAMERA")
        @Dependencies("numpy")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dims = [512, 512]

        @Persistent()
        def behavior(self):
            image = np.random.randn(*self.dims)
            self.buffer.publish(image)
            self.sensed.publish(1)
            time.sleep(1)

    class Processing(Role):
        @Channel(name="result")
        @Channel(name="buffer")
        @Metric(name="processed")
        @Requirements("CPU")
        @KPI("buffer_queue_size[100000000s] < 10")
        @Dependencies("numpy")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Async(image="buffer")
        def behavior(self, image):
            res = np.sum(image)
            self.result.publish(res)
            self.processed.publish(1)
            time.sleep(0.75)
