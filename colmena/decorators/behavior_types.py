#!/usr/bin/env python3
#
#  Copyright 2002-2025 Barcelona Supercomputing Center (www.bsc.es)
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

import time
from typing import Callable
from functools import wraps

from colmena.exceptions import WrongFunctionForDecoratorException
from colmena.logger import Logger


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
                # Loop through all declared channels
                for name, channel_name in self.__channels.items():
                    channel = getattr(self_, channel_name)

                    # Receive loop for each channel (sequential, all in main thread)
                    self.__logger.info(channel)
                    while self_.running:
                        for message in channel.subscriber().receive():
                            func(self_, *args, **kwargs, **{name: message.value})
                            channel.subscriber().ack(message)
            return logic

        raise WrongFunctionForDecoratorException(
            func_name=func.__name__, dec_name="Async"
        )


class Persistent:
    """
    Decorator that specifies that a Role's behavior function
        should be run persistently.
    """

    __slots__ = ["__period", "__logger"]

    def __init__(self, period: int = None):
        self.__period = period
        self.__logger = Logger(self).get_logger()

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ == "behavior":

            @wraps(func)
            def logic(self_, *args, **kwargs):
                # Persistent execution loop (runs in main thread)
                while self_.running:
                    start_time = time.time()

                    func(self_, *args, **kwargs)

                    if self.__period is not None:
                        time.sleep(max(0, self.__period - (time.time() - start_time)))

            return logic

        raise WrongFunctionForDecoratorException(
            func_name=func.__name__, dec_name="Persistent"
        )
