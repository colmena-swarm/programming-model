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
    Service,
    Role,
    Channel,
    Requirements,
    Metric,
    Persistent,
    Async,
    KPI, Data,
)


class ExampleSensorprocessor(Service):
    @Channel(name="images")
    @Channel(name="processed")
    @Metric(name="processing_time")
    @Data(name="num_images")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Sensing(Role):
        @Data(name="num_images")
        @Channel(name="images")
        @Requirements("CAMERA")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dims = [512, 512]
            self.num = 0

        @Persistent()
        def behavior(self):
            image = {
                "payload": np.random.randn(*self.dims),
                "timestamp": time.time(),
            }
            self.images.publish(image)
            self.num_images.publish(self.num)
            self.num += 1
            time.sleep(1)

    class Processing(Role):
        @Data(name="num_images")
        @Channel(name="processed")
        @Channel(name="images")
        @Metric(name="processing_time")
        @Requirements("CPU")
        @KPI("examplesensorprocessor/processing_time[5s] < 1")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Async(image="images")
        def behavior(self, image):
            res = np.sum(image["payload"])
            time.sleep(0.75) #simulate work
            self.processed.publish(res)
            print(self.num_images.get().decode('utf-8'))
            self.processing_time.publish(time.time() - image["timestamp"])
