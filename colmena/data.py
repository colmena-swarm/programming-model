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

import pickle
from typing import Callable
from functools import wraps
from colmena.client import ContextAwareness
from colmena.exceptions import (
    WrongClassForDecoratorException,
    WrongFunctionForDecoratorException,
    DataNotExistException,
)
from colmena.logger import Logger


class Data:
    """
    Decorator that can be used in __init__ functions of Role and Service.
    It has an interface to call functions on the data object.
    """

    def __init__(self, name: str, scope: str = None):
        self.__name = name
        self.__scope = scope
        self.__data_if = DataInterface(name)
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
                    try:
                        service_config = args[0].__init__.config
                        scope = service_config["data"][self.__name]
                    except (AttributeError, KeyError):
                        raise DataNotExistException(data_name=self.__name)

                    try:
                        data = kwargs["data"]
                    except KeyError:
                        data = {}

                    self.__data_if.scope = scope
                    data[self.name] = self.__data_if
                    kwargs["data"] = data

                elif not parent_class_name == "Service":
                    raise WrongClassForDecoratorException(
                        class_name=type(self_).__name__, dec_name="Data"
                    )
                return func(self_, *args, **kwargs)

        else:
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Data"
            )
        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if self.__scope is None:
            try:
                logic.config["data"].append(self.__name)
            except KeyError:
                logic.config["data"] = [self.__name]

        else:
            try:
                logic.config["data"][self.__name] = self.__scope
            except KeyError:
                logic.config["data"] = {self.__name: self.__scope}

        return logic


class DataInterface:
    def __init__(self, name):
        self._name = name
        self._scope = None
        self.__publish_method = None
        self.__get_method = None
        self.__logger = Logger(self).get_logger()

    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, scope):
        self._scope = scope

    def _set_context_awareness(self, context_awareness: ContextAwareness):
        self.__context_awareness = context_awareness

    def _set_publish_method(self, func: Callable):
        self.__publish_method = func

    def _set_get_method(self, func: Callable):
        self.__get_method = func

    def publish(self, value: object):
        self.__context_awareness.publish(key=self._name, value=value, publisher=self.__publish_method)

    def get(self) -> bytes:
        value = self.__get_method(key=self._name)
        return value
