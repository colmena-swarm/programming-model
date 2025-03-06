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

import zenoh

key = "exampleapplication/company_premises"

if __name__ == "__main__":
    session = zenoh.open()
    session.get(key, lambda reply:
        print(f"Received '{reply.ok.key_expr}': '{reply.ok.payload.decode('utf-8')}'")
        if reply.ok is not None else print(f"Received ERROR: '{reply.err.payload.decode('utf-8')}'"))
