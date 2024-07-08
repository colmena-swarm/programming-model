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

import json
from functools import wraps
from colmena.exceptions import (
    FunctionNotImplementedException,
    AttributeNotExistException,
    WrongFunctionForDecoratorException,
    WrongClassForDecoratorException,
)
from typing import Callable
from colmena.logger import Logger


class Context:
    def __init__(self, name=None, scope=None, class_ref=None):
        self.name = name
        self.scope = scope
        self.class_ref = class_ref

        self.logger = Logger(self).get_logger()

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ in ("__init__", "logic"):

            @wraps(func)
            def logic(self_, *args, **kwargs):
                parent_class_name = self_.__class__.__bases__[0].__name__
                if parent_class_name == "Service":
                    _dict_value = self.class_ref()
                elif parent_class_name == "Role":
                    _dict_value = self.scope
                else:
                    raise WrongClassForDecoratorException(
                        class_name=parent_class_name, dec_name="Context"
                    )

                try:
                    self_._context[self.name] = _dict_value
                except AttributeError:
                    self_._context = {self.name: _dict_value}
                return func(self_, *args, **kwargs)

        else:
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name="Context"
            )
        return logic

    def locate(self, device: object):
        """
        Function to locate a device from its object parameters.
        To be reimplemented in subclass.

        :param device: object to retrieve device parameters from
        :return: Position in "structure"
        """
        raise FunctionNotImplementedException(func_name="locate", class_name="Context")

    def get_json(self) -> str:
        """
        Method to get json output from a Context class.
        """
        if not hasattr(self, "structure"):
            raise AttributeNotExistException(
                attr_name="structure", class_name="Context"
            )
        if "locate" not in type(self).__dict__:
            raise FunctionNotImplementedException(
                func_name="locate", class_name="Context"
            )
        return json.dumps(obj=self.structure, indent=4)
