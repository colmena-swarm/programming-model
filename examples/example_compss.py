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
from pycompss.api.api import compss_wait_on
from pycompss.api.container import container
from pycompss.api.task import task
from colmena import (
    Service,
    Role,
    Requirements,
    Persistent,
)

global values
values = [1]

@container(engine="DOCKER", image="increment")
@task(returns=1)
def increment(value):
    return value + 1

class ExampleCompss(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Increment(Role):
        @Requirements("COMPSS")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()   
        def behavior(self):
            global values
            for pos in range(len(values)):
                values[pos] = increment(values[pos])
            values = compss_wait_on(values)
            print(values)
            print("sleeping...")
            time.sleep(1)
