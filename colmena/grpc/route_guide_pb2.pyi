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

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ThresholdType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GREATER_THAN_OR_EQUAL_TO: _ClassVar[ThresholdType]
    LESS_THAN: _ClassVar[ThresholdType]

class HardwareRequirement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAMERA: _ClassVar[HardwareRequirement]
    CPU: _ClassVar[HardwareRequirement]

class TimeUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SECONDS: _ClassVar[TimeUnit]
    MINUTES: _ClassVar[TimeUnit]
    HOURS: _ClassVar[TimeUnit]

GREATER_THAN_OR_EQUAL_TO: ThresholdType
LESS_THAN: ThresholdType
CAMERA: HardwareRequirement
CPU: HardwareRequirement
SECONDS: TimeUnit
MINUTES: TimeUnit
HOURS: TimeUnit

class StorageRequest(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: bytes
    def __init__(
        self, key: _Optional[str] = ..., value: _Optional[bytes] = ...
    ) -> None: ...

class MetricsStorageRequest(_message.Message):
    __slots__ = ("key", "value", "timestamp")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: float
    timestamp: _timestamp_pb2.Timestamp
    def __init__(
        self,
        key: _Optional[str] = ...,
        value: _Optional[float] = ...,
        timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class MetricsQueryRequest(_message.Message):
    __slots__ = ("key", "threshold", "thresholdType")
    KEY_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    THRESHOLDTYPE_FIELD_NUMBER: _ClassVar[int]
    key: str
    threshold: float
    thresholdType: ThresholdType
    def __init__(
        self,
        key: _Optional[str] = ...,
        threshold: _Optional[float] = ...,
        thresholdType: _Optional[_Union[ThresholdType, str]] = ...,
        **kwargs
    ) -> None: ...

class MetricsQueryResponse(_message.Message):
    __slots__ = ("met",)
    MET_FIELD_NUMBER: _ClassVar[int]
    met: bool
    def __init__(self, met: bool = ...) -> None: ...

class GetStoredRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetStoredResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class CommunicationChannelsRequest(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class CommunicationChannelsResponse(_message.Message):
    __slots__ = ("key", "communicationChannels", "colmenaStorageCommunicationChannel")
    KEY_FIELD_NUMBER: _ClassVar[int]
    COMMUNICATIONCHANNELS_FIELD_NUMBER: _ClassVar[int]
    COLMENASTORAGECOMMUNICATIONCHANNEL_FIELD_NUMBER: _ClassVar[int]
    key: str
    communicationChannels: _containers.RepeatedCompositeFieldContainer[
        CommunicationChannel
    ]
    colmenaStorageCommunicationChannel: _containers.RepeatedCompositeFieldContainer[
        ColmenaStorageCommunicationChannel
    ]
    def __init__(
        self,
        key: _Optional[str] = ...,
        communicationChannels: _Optional[
            _Iterable[_Union[CommunicationChannel, _Mapping]]
        ] = ...,
        colmenaStorageCommunicationChannel: _Optional[
            _Iterable[_Union[ColmenaStorageCommunicationChannel, _Mapping]]
        ] = ...,
    ) -> None: ...

class CommunicationChannel(_message.Message):
    __slots__ = ("host", "port")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: int
    def __init__(
        self, host: _Optional[str] = ..., port: _Optional[int] = ...
    ) -> None: ...

class ColmenaStorageCommunicationChannel(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class RegisterCommunicationChannelRequest(_message.Message):
    __slots__ = ("key", "host", "port")
    KEY_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    key: str
    host: str
    port: int
    def __init__(
        self,
        key: _Optional[str] = ...,
        host: _Optional[str] = ...,
        port: _Optional[int] = ...,
    ) -> None: ...

class ServiceDescriptionId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class ServiceDescription(_message.Message):
    __slots__ = ("id", "roleDefinitions", "dockerRoleDefinitions", "kpis")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLEDEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    DOCKERROLEDEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    KPIS_FIELD_NUMBER: _ClassVar[int]
    id: ServiceDescriptionId
    roleDefinitions: _containers.RepeatedCompositeFieldContainer[RoleDefinition]
    dockerRoleDefinitions: _containers.RepeatedCompositeFieldContainer[
        DockerRoleDefinition
    ]
    kpis: _containers.RepeatedCompositeFieldContainer[Kpi]
    def __init__(
        self,
        id: _Optional[_Union[ServiceDescriptionId, _Mapping]] = ...,
        roleDefinitions: _Optional[_Iterable[_Union[RoleDefinition, _Mapping]]] = ...,
        dockerRoleDefinitions: _Optional[
            _Iterable[_Union[DockerRoleDefinition, _Mapping]]
        ] = ...,
        kpis: _Optional[_Iterable[_Union[Kpi, _Mapping]]] = ...,
    ) -> None: ...

class DockerRoleDefinition(_message.Message):
    __slots__ = ("id", "imageId", "hardwareRequirements", "kpis")
    ID_FIELD_NUMBER: _ClassVar[int]
    IMAGEID_FIELD_NUMBER: _ClassVar[int]
    HARDWAREREQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    KPIS_FIELD_NUMBER: _ClassVar[int]
    id: str
    imageId: str
    hardwareRequirements: _containers.RepeatedScalarFieldContainer[HardwareRequirement]
    kpis: _containers.RepeatedCompositeFieldContainer[Kpi]
    def __init__(
        self,
        id: _Optional[str] = ...,
        imageId: _Optional[str] = ...,
        hardwareRequirements: _Optional[
            _Iterable[_Union[HardwareRequirement, str]]
        ] = ...,
        kpis: _Optional[_Iterable[_Union[Kpi, _Mapping]]] = ...,
    ) -> None: ...

class RoleDefinition(_message.Message):
    __slots__ = ("id", "className", "hardwareRequirements", "kpis")
    ID_FIELD_NUMBER: _ClassVar[int]
    CLASSNAME_FIELD_NUMBER: _ClassVar[int]
    HARDWAREREQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    KPIS_FIELD_NUMBER: _ClassVar[int]
    id: str
    className: str
    hardwareRequirements: _containers.RepeatedScalarFieldContainer[HardwareRequirement]
    kpis: _containers.RepeatedCompositeFieldContainer[Kpi]
    def __init__(
        self,
        id: _Optional[str] = ...,
        className: _Optional[str] = ...,
        hardwareRequirements: _Optional[
            _Iterable[_Union[HardwareRequirement, str]]
        ] = ...,
        kpis: _Optional[_Iterable[_Union[Kpi, _Mapping]]] = ...,
    ) -> None: ...

class Kpi(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...
