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

class ChannelNotExistException(Exception):
    """Exception raised when a channel is not defined in the Service class."""

    def __init__(self, channel_name):
        msg = f"Channel '{channel_name}' not defined in Service class."
        super().__init__(msg)


class DataNotExistException(Exception):
    """Exception raised when a data object is not defined in the Service class."""

    def __init__(self, data_name):
        msg = f"Data '{data_name}' not defined in Service class."
        super().__init__(msg)


class MetricNotExistException(Exception):
    """Exception raised when a metric object is not defined in the Service class."""

    def __init__(self, metric_name):
        msg = f"Metric '{metric_name}' not defined in Service class."
        super().__init__(msg)


class WrongClassForDecoratorException(Exception):
    """Exception raised when the class of a function to decorate is invalid."""

    def __init__(self, class_name, dec_name):
        msg = f"Class '{class_name}' cannot be decorated with @{dec_name}"
        super().__init__(msg)


class WrongFunctionForDecoratorException(Exception):
    """Exception raised when the decoration of a function is invalid."""

    def __init__(self, func_name, dec_name):
        msg = f"Function '{func_name}' cannot be decorated with @{dec_name}"
        super().__init__(msg)


class FunctionNotImplementedException(Exception):
    """Exception raised when a function is not implemented."""

    def __init__(self, func_name, class_name):
        msg = f"Function '{func_name}' of class '{class_name}' is not implemented."
        super().__init__(msg)


class AttributeNotExistException(Exception):
    """Exception raised when a class doesn't have an attribute."""

    def __init__(self, attr_name, class_name):
        msg = f"Class '{class_name}' doesn't have attribute '{attr_name}'."
        super().__init__(msg)


class RoleNotExist(Exception):
    """Exception raised when a role doesn't exist in the Service class."""

    def __init__(self, role_name):
        msg = f"Role '{role_name}' doesn't exist."
        super().__init__(msg)


class WrongServiceClassName(Exception):
    """Exception raised if the service class is not named in the right way
    (important in test files).
    """

    def __init__(self, module_name, service_name):
        message = f"Service class in {module_name} should be named {service_name}"
        super().__init__(message)

class ReplicatedDecorator(Exception):
    """Exception raised if the service class is not named in the right way
    (important in test files).
    """

    def __init__(self, decorator_name, role_name):
        message = f"Decorator {decorator_name} is used twice in Role class {role_name}"
        super().__init__(message)

    def __init__(self, decorator_name):
        message = f"Decorator {decorator_name} is used twice."
        super().__init__(message)

class DCPIPMissingException(Exception):
    """Exception raised if the DCP_IP environment variable is not set."""

    def __init__(self):
        message = "IP of the DCP server not indicated."
        super().__init__(message)
