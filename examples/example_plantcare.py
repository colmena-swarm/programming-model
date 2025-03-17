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
    KPI,
)


class ExamplePlantcare(Service):
    @Metric(name="moisture")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Plantsensor(Role):
        @Metric(name="moisture")
        @Requirements("SENSOR")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def read_temp(self):
            return random.randint(15, 30)

        @Persistent()
        def behavior(self):
            self.moisture.publish(self.read_temp())
            time.sleep(1)

    class Plantwatering(Role):
        @Requirements("WATERING")
        @KPI("exampleplantcare/moisture[5s] > 20")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            print("watering ${PLANT_NAME_WATERING_COMPONENT}...")
            time.sleep(1)
