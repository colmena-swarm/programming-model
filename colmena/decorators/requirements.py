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
from colmena.exceptions import (
    WrongClassForDecoratorException,
    WrongFunctionForDecoratorException,
)
from colmena.logger import Logger


class Requirements:
    """Decorator requirements specifies the hardware requirements for each role."""

    __slots__ = ["__expression", "__logger"]

    def __init__(self, expression: str):
        self.__expression = expression
        self.__logger = Logger(self).get_logger()

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ in ("__init__", "logic"):

            def logic(self_, *args, **kwargs):
                parent_class_name = self_.__class__.__bases__[0].__name__
                if parent_class_name == "Role":
                    if not hasattr(self_, "reqs"):
                        self_.reqs = []
                    self_.reqs.append(self.__expression)
                else:
                    raise WrongClassForDecoratorException(
                        class_name=type(self_).__name__, dec_name="Requirements"
                    )
                return func(self_, *args, **kwargs)

        else:
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Requirements"
            )

        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if "reqs" not in logic.config:
            logic.config["reqs"] = []
        logic.config["reqs"].append(self.__expression)

        return logic
