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

import threading
from typing import Callable, TYPE_CHECKING
from functools import wraps
from colmena.utils.exceptions import WrongFunctionForDecoratorException
from colmena.utils.logger import Logger

if TYPE_CHECKING:
    import colmena


class Async:
    """
    Decorator that specifies that a Role's behavior function
        should be run asynchronous with one or several channels.
    """

    __slots__ = ["__channels", "__it", "__logger"]

    def __init__(self, it: int = None, **kwargs):
        self.__channels = kwargs
        self.__logger = Logger(self).get_logger()
        self.__it = it

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ == "behavior":

            @wraps(func)
            def logic(self_, *args, **kwargs):
                for name, channel in self.__channels.items():
                    process = threading.Thread(
                        target=self._behavior,
                        args=(
                            lambda r: func(self_, *args, **kwargs, **r),
                            name,
                            getattr(self_, channel),
                            self_._num_executions,
                        ),
                    )
                    process.start()
                    try:
                        self_._processes.append(process)
                    except AttributeError:
                        self_._processes = []
                        self_._processes.append(process)

            return logic
        raise WrongFunctionForDecoratorException(
            func_name=func.__name__, dec_name="Async"
        )

    def _behavior(
            self,
            func: Callable,
            name: str,
            channel: "colmena.ChannelInterface",
            num_executions: "colmena.MetricInterface",
    ):
        self.__logger.debug("Running async")
        self.call_async(channel.receive(), func, name, num_executions)

    @staticmethod
    def call_async(
            sub,
            func: Callable,
            name: str,
            num_executions: "colmena.MetricInterface",
    ):
        while True:
            for sample in sub.receive():
                message = sample
                func({name: message})
                num_executions.publish(1)


class Persistent:
    """
    Decorator that specifies that a Role's behavior function
        should be run persistently.
    """

    def __init__(self, it: int = None):
        self.__it = it
        self.__logger = Logger(self).get_logger()
        self.__processes = []

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ == "behavior":

            @wraps(func)
            def logic(self_, *args, **kwargs):
                process = threading.Thread(
                    target=self._behavior,
                    args=(lambda: func(self_, *args, **kwargs), self_._num_executions),
                )
                process.start()
                try:
                    self_._processes.append(process)
                except AttributeError:
                    self_._processes = []
                    self_._processes.append(process)

            return logic
        raise WrongFunctionForDecoratorException(
            func_name=func.__name__, dec_name="Persistent"
        )

    def _behavior(self, func: Callable, num_executions: "colmena.MetricInterface"):
        self.__logger.debug("Running persistent")
        if self.__it is None:
            while True:
                self.call_persistent(func, num_executions)
        else:
            for _ in range(self.__it):
                self.call_persistent(func, num_executions)

    @staticmethod
    def call_persistent(func, num_executions):
        func()
        num_executions.publish(1)
