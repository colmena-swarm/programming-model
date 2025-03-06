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
from colmena import (
    Context,
    Service,
    Role,
    Channel,
    Requirements,
    Metric,
    Persistent,
    Async,
    KPI, Dependencies, Version
)


class CompanyPremises(Context):
    @Dependencies("numpy")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structure = {
            "floor1": ["reception"],
            "floor2": ["reception", "open_space"],
            "floor3": ["open_space", "manager_office"],
        }

    def locate(self, device):
        print(self.structure["floor1"][0])


class ExampleApplication(Service):
    @Context("company_premises", class_ref=CompanyPremises)
    @Channel("buffer", " ")
    @Channel("result", " ")
    @Metric("sensed")
    @Metric("processed")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Sensing(Role):
        @Version("0.1")
        @Dependencies("numpy")
        @Context("company_premises", "*.*.lobby")
        @Channel("buffer")
        @Metric("sensed")
        @Requirements("CAMERA")
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
        @Dependencies("numpy")
        @Channel("result")
        @Channel("buffer")
        @Metric("processed")
        @Requirements("CPU")
        @KPI("buffer_queue_size[100000000s] < 10")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Async(image="buffer")
        def behavior(self, image):
            res = np.sum(image)
            self.result.publish(res)
            self.processed.publish(1)
            time.sleep(0.75)
