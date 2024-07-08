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
import os
from sys import modules
import importlib.util
import shutil
from typing import Dict, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    import colmena

cwd = os.getcwd()


def build(
    module_name: str,
    service_name: str,
    project_path: str,
    service_code_path: str,
    username: str,
):
    """
    Creates the folder with the build files, including source code, service description, and Dockerfile.

    Parameters:
        module_name: python module name
        service_name: service class name
        project_path: path to the colmena project
        service_code_path: path to the service code
        username: DockerHub user
    """
    clean(f"{service_code_path}/{module_name}")
    service = get_service(module_name, service_name, service_code_path)()
    roles = service.get_role_names()
    build_temp_folders(
        module_name,
        service_name,
        roles,
        service.context,
        project_path,
        service_code_path,
    )
    tags = {}
    for role_name in roles:
        tags[role_name] = f"{username}/colmena-{lowercase(role_name)}"

    if service.context is not None:
        for context in service.context.keys():
            tags[context] = f"{username}/colmena-{lowercase(context)}"

        write_service_description(
            f"{service_code_path}/{module_name}/build",
            tags,
            roles,
            service,
            service.context.keys(),
        )
    else:
        write_service_description(
            f"{service_code_path}/{module_name}/build",
            tags,
            roles,
            service,
            None,
        )



def build_temp_folders(
    module_name: str,
    service_name: str,
    roles: List[str],
    contexts: Dict[str, "colmena.Context"],
    project_path: str,
    service_code_path: str,
):
    """
    Builds the temp folders:
        - build
            - role_name
                - colmena/
                - module_name.py
                - main.py
                - pyproject.toml
                - README.md
            - service_description.json

    Parameters:
        module_name: python module name
        service_name: service class name
        roles: list of role names in the service
        contexts: dict with service's context objects
        project_path: path to colmena project
        service_code_path: path to the service code
    """
    os.mkdir(f"{service_code_path}/{module_name}")
    os.mkdir(f"{service_code_path}/{module_name}/build")

    if contexts is not None:
        os.mkdir(f"{service_code_path}/{module_name}/build/context")
        for context_key, context_value in contexts.items():
            path = f"{service_code_path}/{module_name}/build/context/{context_key}"
            copy_files(path, service_code_path, module_name, project_path)
            create_main_context(path, module_name, type(context_value).__name__)
            write_dockerfile(path)

    for role_name in roles:
        path = f"{service_code_path}/{module_name}/build/{role_name}"
        copy_files(path, service_code_path, module_name, project_path)
        create_main(path, module_name, service_name, role_name)
        write_dockerfile(path)


def copy_files(path: str, service_code_path: str, module_name: str, project_path: str):
    os.mkdir(path)
    shutil.copyfile(f"{service_code_path}/{module_name}.py", f"{path}/{module_name}.py")
    shutil.copytree(f"{project_path}/colmena", f"{path}/colmena")
    shutil.copy(f"{project_path}/pyproject.toml", path)
    shutil.copy(f"{project_path}/README.md", path)


def create_main(path: str, module_name: str, service_name: str, role_name: str):
    """
    Creates the main file of a role.

    Parameters:
        path: path of the role inside the build folder
        module_name: module name of the application
        service_name: name of the service class
        role_name: name of the role
    """
    with open(f"{path}/main.py", "w") as f:
        print(f"from {module_name} import {service_name}\n\n", file=f)
        print("if __name__ == '__main__':", file=f)
        print(f"\tr = {service_name}.{role_name}({service_name})", file=f)
        print("\tr.execute()", file=f)


def create_main_context(path: str, module_name: str, context_name: str):
    with open(f"{path}/main.py", "w") as f:
        print(f"from {module_name} import {context_name}\n\n", file=f)
        print("if __name__ == '__main__':", file=f)
        print("\tdevice = None # Environment variable, JSON file, TBD.", file=f)
        print(f"\tr = {context_name}().locate(device)", file=f)


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


def write_dockerfile(path: str):
    """
    Writes Dockerfile.

    Parameters:
        - path: path to the Dockerfile
    """
    with open(f"{path}/Dockerfile", "w") as f:
        print("FROM python:3.9.18-slim-bookworm", file=f)
        print("COPY . /home", file=f)
        print("WORKDIR /home", file=f)
        print("RUN python3 -m pip install .", file=f)
        print("ENTRYPOINT python3 -m main", file=f)


def write_service_description(
    path: str,
    image_ids: Dict[str, str],
    role_names: List[str],
    service: "colmena.Service",
    context_names: List[str],
):
    """
    Writes service description json.

    Parameters:
        - path: build path
        - image_ids: path of all role folders
        - role_names: list of role names
        - service: service class
    """
    output = {"id": {"value": type(service).__name__}}

    if context_names is not None:
        contexts = []
        for context in context_names:
            c = {"id": context, "imageId": image_ids[context]}
            contexts.append(c)
        output["dockerContextDefinitions"] = contexts

    roles = []
    for role_name in role_names:
        r = {"id": role_name, "imageId": image_ids[role_name]}
        if "reqs" in service.config[role_name]:
            r["hardwareRequirements"] = service.config[role_name]["reqs"]
        else:
            r["hardwareRequirements"] = []
        if "kpis" in service.config[role_name]:
            r["kpis"] = service.config[role_name]["kpis"]
        else:
            r["kpis"] = []
        roles.append(r)

    if "kpis" in service.config["kpis"]:
        output["kpis"] = service.config["kpis"]
    else:
        output["kpis"] = []

    output["dockerRoleDefinitions"] = roles
    with open(f"{path}/service_description.json", "w") as f:
        json.dump(output, f, indent=4)


def clean(path: str):
    """Deletes build folders and files."""
    if os.path.isdir(path):
        shutil.rmtree(path)


def lowercase(image_tag: str) -> str:
    """Docker does not accept image tags starting with a capital letter."""
    return image_tag.lower()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--colmena_path",
        help="Path to the service code",
        default="..",
    )
    parser.add_argument(
        "--service_code_path",
        help="Path to the service code",
        default="../test/examples",
    )
    parser.add_argument("--module_name", help="Name of the python module")
    parser.add_argument("--service_name", help="Name of the service class")
    parser.add_argument("--username", help="Docker username")

    args = parser.parse_args()
    sys.path.append(args.colmena_path)
    build(
        module_name=args.module_name,
        service_name=args.service_name,
        project_path=args.colmena_path,
        service_code_path=args.service_code_path,
        username=args.username,
    )
