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

# -*- coding: utf-8 -*-

import glob
import os
import json
import subprocess
from sys import modules
from typing import List, Callable

import importlib

import pytest

from colmena.building_tool.colmena_build import (
    clean,
    create_build_folders,
    write_service_description,
    build,
)
from colmena.exceptions import WrongServiceClassName


class TestBuild:

    @pytest.fixture(autouse=True)
    def setup_folder(self, folder):
        self.folder = folder

    def test_build_files(self):
        """Builds files from all services."""
        files = self.get_files()
        for f in files:
            self.build_files(*self.get_module_and_service_names(f))

    def build_files(
            self, module_name: str, service_name: str
    ):
        """
        Builds files from one service

        Attributes:
            module_name: name of the python module
            service_name: name of the service class
        """
        clean(f"{self.folder}/{module_name}")
        try:
            service = get_service(
                module_name, service_name, service_code_path=self.folder
            )()
        except AttributeError as exc:
            raise WrongServiceClassName(module_name, service_name) from exc
        roles = service.get_role_names()
        create_build_folders(
            module_name=module_name,
            service_name=service_name,
            roles=roles,
            contexts=service.context,
            service_code_path=self.folder,
            config=service.config
        )
        build_path = f"{self.folder}/{module_name}/build"
        assert os.path.isdir(build_path)
        tags = {}
        for role_name in roles:
            path = f"{build_path}/{role_name}"
            assert os.path.isdir(path)
            assert os.path.isfile(path + "/Dockerfile")
            assert os.path.isfile(path + "/pyproject.toml")
            assert os.path.isfile(path + "/requirements.txt")
            assert os.path.isfile(path + f"/{role_name}/main.py")
            assert os.path.isfile(path + f"/{role_name}/{module_name}.py")
            try:
                version = service.config[role_name]['version']
            except KeyError:
                version = 'latest'
            tags[role_name] = f"{role_name.lower()}:{version}"

        if service.context is not None:
            for context_name in service.context.keys():
                path = f"{build_path}/context/{context_name}"
                assert os.path.isdir(path)
                assert os.path.isfile(path + "/Dockerfile")
                assert os.path.isfile(path + "/pyproject.toml")
                assert os.path.isfile(path + "/requirements.txt")
                assert os.path.isfile(path + f"/{context_name}/main.py")
                assert os.path.isfile(path + f"/{context_name}/{module_name}.py")
                try:
                    version = service.context[context_name].version
                except AttributeError:
                    version = 'latest'
                tags[context_name] = f"{context_name.lower()}:{version}"

            write_service_description(build_path, tags, roles, service, service.context.keys())
        else:
            write_service_description(build_path, tags, roles, service, None)

        with open(f"{build_path}/service_description.json") as f1, open(f"{self.folder}/{module_name}.json") as f2:
            assert json.load(f1) == json.load(f2)

    def remove_built_files(self, dist_path):
        if os.path.exists(dist_path) and os.path.isdir(dist_path):
            files_to_remove = glob.glob(f"{dist_path}/colmena*")

            for file_path in files_to_remove:
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def build_package(self, path):
        subprocess.check_call(["python3", "-m", "build", path])

    def get_files(self) -> List:
        """Gets all python files from the folder example/."""
        files = []
        for f in os.listdir(self.folder):
            if f.endswith(".py"):
                files.append(f)
        return files

    def get_module_and_service_names(self, file_name: str) -> [str, str]:
        """Gets module name and service class name from python file."""
        module_name = os.path.splitext(file_name)[0]
        name = module_name.replace("_", " ").split()[1]
        service_name = f"Example{name.capitalize()}"
        return module_name, service_name


def get_service(
        module_name: str, service_name: str, service_code_path: str
) -> Callable:
    """
    Gets service class.

    Parameters:
        - module_name: name of the python module
        - service_name: name of the service class
        - service_code_path: path to the service code
    """
    path = f"{service_code_path}/{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    service_module = importlib.util.module_from_spec(spec)
    modules["module.name"] = service_module
    spec.loader.exec_module(service_module)
    return getattr(service_module, service_name)
