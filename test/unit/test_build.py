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

import os
import filecmp
from typing import List

import pytest

from scripts.colmena_build import (
    clean,
    build_temp_folders,
    write_service_description,
    get_service,
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
        build_temp_folders(
            module_name=module_name,
            service_name=service_name,
            roles=roles,
            contexts=service.context,
            project_path="../../",
            service_code_path=self.folder,
        )
        build_path = f"{self.folder}/{module_name}/build"
        assert os.path.isdir(build_path)
        tags = {}
        for role in roles:
            path = f"{build_path}/{role}"
            assert os.path.isdir(path)
            assert os.path.isfile(path + "/Dockerfile")
            assert os.path.isfile(path + "/main.py")
            assert os.path.isfile(path + f"/{module_name}.py")
            assert os.path.isdir(path + "/colmena")
            assert os.path.isfile(path + "/pyproject.toml")
            assert os.path.isfile(path + "/README.md")
            tags[role] = f"colmena/test{role.lower()}"

        if service.context is not None:
            for context_name in service.context.keys():
                path = f"{build_path}/context/{context_name}"
                assert os.path.isdir(path)
                assert os.path.isfile(path + "/Dockerfile")
                assert os.path.isfile(path + "/main.py")
                assert os.path.isfile(path + f"/{module_name}.py")
                assert os.path.isdir(path + "/colmena")
                assert os.path.isfile(path + "/pyproject.toml")
                assert os.path.isfile(path + "/README.md")
                tags[context_name] = f"colmena/test{context_name.lower()}"

            write_service_description(build_path, tags, roles, service, service.context.keys())
        else:
            write_service_description(build_path, tags, roles, service, None)

        assert filecmp.cmp(
            f"{build_path}/service_description.json",
            f"{self.folder}/{module_name}.json",
        )

    def test_build(self):
        """
        Builds all services,
        uploading docker images to DockerHub (must have dockerhub.properties file).
        """
        files = self.get_files()
        for f in files:
            self._build(*self.get_module_and_service_names(f))

    def _build(
            self, module_name: str, service_name: str
    ):
        """Builds one service, uploading one docker image per role."""
        clean(module_name)
        build(
            module_name=module_name,
            service_name=service_name,
            project_path="../../",
            service_code_path=self.folder,
        )

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
