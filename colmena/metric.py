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

from typing import Callable
from functools import wraps
from colmena.utils.exceptions import (
    WrongClassForDecoratorException,
    WrongFunctionForDecoratorException,
    MetricNotExistException,
)
from colmena.utils.logger import Logger


class Metric:
    """
    Decorator that can be used in __init__ functions of Role and Service.
    It has an interface to call functions on the metric object.
    """

    def __init__(self, name: str):
        self.__name = name
        self.__metric_if = MetricInterface(name)
        self.__logger = Logger(self).get_logger()

    @property
    def name(self):
        return self.__name

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ in ("__init__", "logic"):

            @wraps(func)
            def logic(self_, *args, **kwargs):
                parent_class_name = self_.__class__.__bases__[0].__name__
                if parent_class_name == "Role":
                    service_config = args[0].__init__.config
                    if (
                        "metrics" not in service_config
                        or self.__name not in service_config["metrics"]
                    ):
                        raise MetricNotExistException(self.__name)

                    try:
                        metrics = kwargs["metrics"]
                    except KeyError:
                        metrics = {}
                    metrics[self.__name] = self.__metric_if
                    kwargs["metrics"] = metrics

                elif not parent_class_name == "Service":
                    raise WrongClassForDecoratorException(
                        class_name=type(self_).__name__, dec_name="Metric"
                    )

                return func(self_, *args, **kwargs)

        else:
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Metric"
            )

        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if "metrics" not in logic.config:
            logic.config["metrics"] = []
        logic.config["metrics"].append(self.__name)
        return logic


class MetricInterface:
    def __init__(self, name):
        self.name = name
        self.__publish_method = None
        self.__logger = Logger(self).get_logger()

    def _set_publish_method(self, func: Callable):
        self.__publish_method = func

    def publish(self, value: float):
        self.__publish_method(key=self.name, value=value)
