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
from colmena.exceptions import (
    WrongClassForDecoratorException,
    WrongFunctionForDecoratorException,
    ChannelNotExistException,
)
from colmena.logger import Logger


class Channel:
    """
    Decorator that can be used in __init__ functions of Role and Service.
    It has an interface to call functions on the channel object.
    """

    def __init__(self, name: str, scope: str = None):
        self.__name = name
        self.__scope = scope
        self.__logger = Logger(self).get_logger()

    @property
    def name(self):
        return self.__name

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ not in ("__init__", "logic"):
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Channel"
            )

        @wraps(func)
        def logic(self_, *args, **kwargs):
            parent_class_name = self_.__class__.__bases__[0].__name__

            if parent_class_name != "Role" and parent_class_name != "Service":
                raise WrongClassForDecoratorException(
                    class_name=type(self_).__name__, dec_name="Channel"
                )

            if parent_class_name == "Role":
                kwargs = self.role_decorator_call(*args, **kwargs)
            return func(self_, *args, **kwargs)

        self.add_config_to_logic(logic, func)
        return logic

    def role_decorator_call(self, *args, **kwargs):
        try:
            service_config = args[0].__init__.config
            scope = service_config["channels"][self.__name]
        except (AttributeError, KeyError) as exc:
            raise ChannelNotExistException(channel_name=self.__name) from exc

        try:
            channels = kwargs["channels"]
        except KeyError:
            channels = {}

        channels[self.__name] = scope
        kwargs["channels"] = channels
        return kwargs

    def add_config_to_logic(self, logic, func):
        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if self.__scope is None:  # If there is no scope defined (Role)
            try:
                logic.config["channels"].append(self.__name)
            except KeyError:
                logic.config["channels"] = [self.__name]

        else:  # If scope is defined (Service)
            try:
                logic.config["channels"][self.__name] = self.__scope
            except KeyError:
                logic.config["channels"] = {self.__name: self.__scope}
