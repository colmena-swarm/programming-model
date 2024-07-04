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

from google.protobuf.timestamp_pb2 import Timestamp
from colmena.grpc import route_guide_pb2_grpc, route_guide_pb2


class ColmenaClient:
    def __init__(self, stub: route_guide_pb2_grpc.ColmenaPlatformStub):
        self.__stub = stub

    def publish_message(self, channel_name: str, message: bytes) -> str:
        request = route_guide_pb2.StorageRequest(key=channel_name, value=message)
        self.__stub.Publish(request)
        msg = f"New object published to '{channel_name}'"
        return msg

    def subscribe(self, channel_name: str) -> bytes:
        request = route_guide_pb2.GetStoredRequest(key=channel_name)
        return self.__stub.GetSubscriptionItem(request).value

    def publish_data(self, data_name: str, data_value: bytes) -> str:
        request = route_guide_pb2.StorageRequest(key=data_name, value=data_value)
        self.__stub.Store(request)
        msg = f"New data value stored: '{data_name}'"
        return msg

    def get_data(self, data_name: str) -> bytes:
        request = route_guide_pb2.GetStoredRequest(key=data_name)
        data_value = self.__stub.GetStored(request).value
        return data_value

    def publish_metric(
        self,
        metric_name: str,
        metric_value: float,
    ) -> str:
        metric_request = route_guide_pb2.MetricsStorageRequest(
            key=metric_name, value=metric_value, timestamp=Timestamp().GetCurrentTime()
        )
        self.__stub.StoreMetrics(metric_request)
        msg = f"New metric value pushed: '{metric_name} = {str(metric_value)}'"
        return msg
