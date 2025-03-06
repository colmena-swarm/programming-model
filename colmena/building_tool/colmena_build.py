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
import shutil
from typing import Dict, List
import colmena


def build(
        service_module_path: str, colmena_build_path : str = None):
    """
    Creates the folder with the build files, including source code, service description, and Dockerfile.

    Parameters:
        service_module_path: path to the service code file
    """
    module_name = os.path.basename(service_module_path).split(".")[0]

    from importlib.machinery import SourceFileLoader

    loader = SourceFileLoader(module_name, service_module_path).load_module()
    for class_name, class_obj in loader.__dict__.items():
        if isinstance(class_obj, type) and issubclass(class_obj, colmena.Service) and class_obj is not colmena.Service:
            service_class = class_obj
            service_name = class_name
            break

    service_code_path = '/'.join(service_module_path.split('/')[:-1])
    clean(f"{service_code_path}/{module_name}")
    service = service_class()
    roles = service.get_role_names()

    create_build_folders(
        module_name,
        service_name,
        roles,
        service.config,
        service.context,
        service_code_path,
        colmena_build_path
    )
    tags = {}
    for role_name in roles:
        try:
            version = service.config[role_name]['version']
        except KeyError:
            version = 'latest'
        tags[role_name] = f"{lowercase(role_name)}:{version}"

    if service.context is not None:
        for context_name in service.context.keys():
            try:
                version = service.context[context_name].version
            except AttributeError:
                version = 'latest'
            tags[context_name] = f"{lowercase(context_name)}:{version}"

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


def write_dependencies(path: str, dependencies: list[str], colmena_build_path: str = None):
    with open(f"{path}/requirements.txt", "w") as file:
        if colmena_build_path is None:
            file.write(f"colmena-swarm-pm[role]=={colmena.__version__}\n")
        else:
            file.write(f"colmena-swarm-pm[role] @ file://{colmena_build_path}\n")
        if dependencies is not None:
            file.write("\n".join(dependencies))


def create_build_folders(
        module_name: str,
        service_name: str,
        roles: List[str],
        config: Dict,
        contexts: Dict[str, "colmena.Context"],
        service_code_path: str,
        colmena_build_path: str = None
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
        service_code_path: path to the service code
    """
    os.mkdir(f"{service_code_path}/{module_name}")
    os.mkdir(f"{service_code_path}/{module_name}/build")

    project_path = '/'.join(colmena.__file__.split('/')[:-1])
    if contexts is not None:
        os.mkdir(f"{service_code_path}/{module_name}/build/context")
        for context_key, context_value in contexts.items():
            path = f"{service_code_path}/{module_name}/build/context/{context_key}"
            copy_files(context_key, path, service_code_path, module_name, project_path)
            try:
                write_dependencies(path, context_value.dependencies, colmena_build_path)
            except AttributeError:
                write_dependencies(path, None, colmena_build_path)
            try:
                version = context_value.version
            except AttributeError:
                version = '0.0.0'
            create_main_context(f"{path}/{context_key}", module_name, type(context_value).__name__, version)

    for role_name in roles:
        path = f"{service_code_path}/{module_name}/build/{role_name}"
        copy_files(role_name, path, service_code_path, module_name, project_path)
        try:
            write_dependencies(path, config[role_name]['dependencies'], colmena_build_path)
        except KeyError:
            write_dependencies(path, None, colmena_build_path)
        try:
            version = config[role_name]['version']
        except KeyError:
            version = '0.0.0'
        create_main(f"{path}/{role_name}", module_name, service_name, role_name, version)


def copy_files(package_name: str, path: str, service_code_path: str, module_name: str, project_path: str):
    shutil.copytree(f"{project_path}/templates", path)
    os.mkdir(f"{path}/{package_name}")
    shutil.copyfile(f"{service_code_path}/{module_name}.py", f"{path}/{package_name}/{module_name}.py")
    adapt_name(path.split("/")[-1], f"{path}/pyproject.toml")


def create_main(path: str, module_name: str, service_name: str, role_name: str, version: str):
    """
    Creates the main file of a role.

    Parameters:
        path: path of the role inside the build folder
        module_name: module name of the application
        service_name: name of the service class
        role_name: name of the role
    """
    with open(f"{path}/main.py", "w") as f:
        print(f"from .{module_name} import {service_name}\n\n", file=f)
        print(f"__version__ = '{version}'", file=f)
        print("def main():", file=f)
        print(f"\tr = {service_name}.{role_name}({service_name})", file=f)
        print("\tr.execute()", file=f)


def create_main_context(path: str, module_name: str, context_name: str, version: str):
    with open(f"{path}/main.py", "w") as f:
        print(f"from .{module_name} import {context_name}\n\n", file=f)
        print(f"__version__ = '{version}'", file=f)
        print("def main():", file=f)
        print("\tdevice = None # Environment variable, JSON file, TBD.", file=f)
        print(f"\tr = {context_name}().locate(device)", file=f)


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


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--service_path",
        help="Path to the service code",
        default="examples/example_cameraprocessors.py",
    )

    args = parser.parse_args()

    print(f"Building service: {args.service_path}")

    build(
        service_module_path=args.service_path
    )


def adapt_name(name, path):
    """Replace the keyword with name in a specific file.

    Args:
        name (str): Name to personalize the file content.
        path (str): Path to the file.
    """
    # Open the file
    with open(path, "r") as file_descriptor:
        content = file_descriptor.read()

    # Replace keywords with the provided name
    content = content.replace("NAME", name)

    # Write the modified content back to the file
    with open(path, "w") as file_descriptor:
        file_descriptor.write(content)


if __name__ == "__main__":
    main()
