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
import requests
from colmena import (
    Service,
    Role,
    Requirements,
    Persistent,
    Data, Context, Dependencies
)

class Grouping(Context):
    @Dependencies("requests")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def locate(self, device):
        device_id = os.getenv("AGENT_ID", "a")
        url = f'http://localhost:12442?device_id={device_id}'
        response = requests.get(url)
        if response.status_code == 200:
            location = response.json()
            print(json.dumps(location))
        else:
            print(response)

class GroupingTest(Service):
    @Context(class_ref=Grouping, name="group")
    @Data(name="leader_id", scope="group/id = .")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Leader(Role):
        @Dependencies("requests")
        @Requirements("LEADER")
        @Context(class_ref=Grouping, name="group")
        @Data(name="leader_id", scope="group/id = .")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            device_id = os.getenv("COMPOSE_PROJECT_NAME", "default_device_id")
            self.leader_id.publish(device_id)
            time.sleep(10)


    class Follower(Role):
        @Dependencies("requests")
        @Requirements("FOLLOWER")
        @Context(class_ref=Grouping, name="group")
        @Data(name="leader_id", scope="group/id = .")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @Persistent()
        def behavior(self):
            leader_id = self.leader_id.get()
            print(leader_id)
            time.sleep(10)
