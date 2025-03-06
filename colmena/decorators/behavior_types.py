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
import time
from typing import Callable, TYPE_CHECKING
from functools import wraps

from colmena.exceptions import WrongFunctionForDecoratorException
from colmena.logger import Logger

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
                            self_
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
            role: "colmena.Role",
    ):
        self.__logger.debug("Running async")
        self.call_async(channel.receive(), func, name, num_executions, role)

    def call_async(self,
            sub,
            func: Callable,
            name: str,
            num_executions: "colmena.MetricInterface",
            role
    ):
        while role.running:
            for message in sub.receive():
                func({name: message.value})
                num_executions.publish(1)
                sub.ack(message)


class Persistent:
    """
    Decorator that specifies that a Role's behavior function
        should be run persistently.
    """

    def __init__(self, period: int = None):
        self.__period = period
        self.__logger = Logger(self).get_logger()
        self.__processes = []

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ == "behavior":

            @wraps(func)
            def logic(self_, *args, **kwargs):
                process = threading.Thread(
                    target=self._behavior,
                    args=(lambda: func(self_, *args, **kwargs), self_._num_executions, self_),
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

    def _behavior(self, func: Callable, num_executions: "colmena.MetricInterface", role: "colmena.Role"):
        self.__logger.debug("Running persistent")

        while role.running:
            start_time = time.time()
            self.call_persistent(func, num_executions)

            elapsed_time = time.time() - start_time
            if (self.__period is not None):
                print("First sleep")
                time.sleep(max(0, self.__period - elapsed_time))

    @staticmethod
    def call_persistent(func, num_executions):
        func()
        num_executions.publish(1)
