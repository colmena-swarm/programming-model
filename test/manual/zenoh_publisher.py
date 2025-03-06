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

import zenoh

key = "dockerContextDefinitions/company_premises"
value = "test_scope"

def increasing_values():
    session = zenoh.open()
    pub = session.declare_publisher(key)
    i = 0
    while True:
        buf = f"{i}"
        print(f"Putting Data ('{key}': '{buf}')...")
        pub.put(buf)
        i += 1
        time.sleep(1)

def single_value():
    session = zenoh.open()
    session.put(key, value)

if __name__ == "__main__":
    increasing_values()
