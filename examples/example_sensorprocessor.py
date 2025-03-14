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
import numpy as np
from colmena import (
    Service,
    Role,
    Channel,
    Requirements,
    Metric,
    Persistent,
    Async,
    KPI, Data, Context,
)

class Device(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def locate(self, device):
        location = {"id": os.getenv("COMPOSE_PROJECT_NAME", "default_device_id")}
        print(json.dumps(location))

class ExampleSensorprocessor(Service):
    @Context(class_ref=Device, name="device")
    @Data(name="images", scope="device/id = .")
    @Metric(name="processing_time")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Sensing(Role):
        @Context(class_ref=Device, name="device")
        @Data(name="images", scope="device/id = .")
        @Requirements("SENSOR")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            payload = "test_string"
            image = {
                "payload": payload,
                "timestamp": time.time(),
            }
            self.images.publish(image)
            print(f"stored {payload} in shared data")
            time.sleep(1)

    class Processing(Role):
        @Context(class_ref=Device, name="device")
        @Data(name="images", scope="device/id = .")
        @Metric(name="processing_time")
        @Requirements("CPU")
        @KPI("examplesensorprocessor/processing_time[5s] < 1")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            image = json.loads(self.images.get().decode('utf-8'))
            shared_data_payload = image["payload"]
            print(f"Load from shared data {shared_data_payload}")
            time.sleep(0.75) #simulate work
            self.processing_time.publish(time.time() - image["timestamp"])
