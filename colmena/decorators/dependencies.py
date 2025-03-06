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

from colmena.exceptions import (
    WrongFunctionForDecoratorException,
    WrongClassForDecoratorException, ReplicatedDecorator,
)
from typing import Callable
from colmena.logger import Logger


class Dependencies:
    """Decorator Dependencies specifies the PyPI dependencies for each role or context."""

    __slots__ = ["__dependencies", "__logger"]

    def __init__(self, *dependencies: str):
        self.__dependencies = [*dependencies]
        self.__logger = Logger(self).get_logger()

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ in ("__init__", "logic"):

            def logic(self_, *args, **kwargs):
                parent_class_name = self_.__class__.__bases__[0].__name__
                if parent_class_name == "Role" or parent_class_name == "Context":
                    if hasattr(self_, "dependencies"):
                        return ReplicatedDecorator("Dependencies", self_.__class__)
                    self_.dependencies = self.__dependencies
                else:
                    raise WrongClassForDecoratorException(
                        class_name=parent_class_name, dec_name="Dependencies"
                    )
                return func(self_, *args, **kwargs)

        else:
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Dependencies"
            )

        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if hasattr(logic, "dependencies"):
            return ReplicatedDecorator("Dependencies")
        logic.config["dependencies"] = self.__dependencies

        return logic

