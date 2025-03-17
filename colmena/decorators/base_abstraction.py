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
from colmena.exceptions import DataNotExistException, ChannelNotExistException, MetricNotExistException, \
    WrongFunctionForDecoratorException, WrongClassForDecoratorException

from colmena.logger import Logger

from functools import wraps
from typing import Callable

class BaseAbstractionDecorator:
    """
    Base decorator for Data, Channel, and Metric decorators.
    Handles shared logic for decorating __init__ or logic methods in Role or Service classes.
    """

    def __init__(self, name: str, kind: str, scope: str = None):
        """
        :param name: The name of the data/channel/metric.
        :param kind: One of 'data', 'channel', or 'metric'.
        :param scope: Optional scope string (used only for data and channel).
        """
        self._name = name
        self._kind = kind  # 'data', 'channel', or 'metric'
        self._scope = scope
        self._logger = Logger(self).get_logger()

        # Metrics never have a scope, override scope to None forcibly
        if self._kind == "metric":
            self._scope = None

    @property
    def name(self):
        return self._name

    def __call__(self, func: Callable) -> Callable:
        if func.__name__ not in ("__init__", "logic"):
            raise WrongFunctionForDecoratorException(
                func_name=func.__name__, dec_name=self._kind.capitalize()
            )

        @wraps(func)
        def logic(self_, *args, **kwargs):
            # Determine if this is a Role or Service class
            parent_class_name = self_.__class__.__bases__[0].__name__

            if parent_class_name == "Role":
                kwargs = self._handle_role(*args, **kwargs)

            elif parent_class_name != "Service":
                raise WrongClassForDecoratorException(
                    class_name=type(self_).__name__,
                    dec_name=self._kind.capitalize()
                )

            return func(self_, *args, **kwargs)

        # Add static config dictionary at decoration time
        self._add_to_config(logic, func)

        return logic

    def _handle_role(self, *args, **kwargs):
        """
        Logic that runs when decorating a Role's __init__ or logic function.
        Extracts service-level config to verify the element exists,
        and attaches it to the kwargs under the correct key.
        """
        try:
            service_config = args[0].__init__.config

            # Use renamed keys for config and kwargs
            if self._kind == "metric":
                key = "metric_info"
            else:
                key = self._kind + "_info"

            if key not in service_config or self._name not in service_config[key]:
                raise self._not_exist_exception()
        except AttributeError:
            raise self._not_exist_exception()

        if self._kind == "metric":
            # Metrics are stored as a list (singular 'metric_info')
            container = kwargs.get("metric_info", [])
            container.append(self._name)
            kwargs["metric_info"] = container
        else:
            # Data and Channel decorators store scoped values in a dict
            container = kwargs.get(key, {})
            container[self._name] = service_config[key][self._name]
            kwargs[key] = container

        return kwargs

    def _add_to_config(self, logic, func):
        """
        Adds the decorator's metadata to the decorated function's config dictionary.
        This is run at decoration time, allowing access to config without instantiating the class.

        Handles Role (list of names) and Service (dict of name:scope) cases.
        """

        try:
            logic.config = func.config
        except AttributeError:
            logic.config = {}

        if self._kind == "metric":
            # Metric always singular key 'metric_info' and always list, no scope
            if "metric_info" not in logic.config:
                logic.config["metric_info"] = []
            logic.config["metric_info"].append(self._name)
            return

        # For data and channel, renamed keys
        key = self._kind + "_info"

        if self._scope is None:
            # No scope specified — Role or Service without scope

            try:
                if isinstance(logic.config[key], list):
                    # Role case: append to list
                    logic.config[key].append(self._name)
                else:
                    # Service case: dict without scope, assign None
                    logic.config[key][self._name] = None
            except KeyError:
                # Key missing — create list (default to Role)
                logic.config[key] = [self._name]

        else:
            # Scope specified — Service decorator, use dict

            try:
                if isinstance(logic.config[key], list):
                    # Convert list to dict with None values before adding scope
                    logic.config[key] = {name: None for name in logic.config[key]}
                logic.config[key][self._name] = self._scope
            except KeyError:
                logic.config[key] = {self._name: self._scope}

    def _not_exist_exception(self):
        """
        Returns the appropriate exception class instance when a decorator target is missing in config.
        """
        if self._kind == "data":
            return DataNotExistException(data_name=self._name)
        elif self._kind == "channel":
            return ChannelNotExistException(channel_name=self._name)
        elif self._kind == "metric":
            return MetricNotExistException(self._name)
        else:
            raise ValueError(f"Unknown kind: {self._kind}")
