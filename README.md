# COLMENA Programming Model
This GitHub repository contains all the files and software necessary to create applications to be deployed on a COLMENA platform. COLMENA (COLaboración entre dispositivos Mediante tecnología de ENjAmbre) aims to ease the development, deployment, operation and maintenance of extremely-high available, reliable and intelligent services running seamlessly across the device-edge-cloud continuum. It leverages a swarm approach organising a dynamic group of autonomous, collaborative nodes following an agile, fully-decentralised, robust, secure and trustworthy open architecture.

## Table of Contents
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)


## Repository Structure
The repository is organized into the following directories and files:

### Directories
- **colmena**: Contains the python library with the programming model and abstractions.
- **examples**: Example applications used for testing.
- **scripts**: Scripts to create a COLMENA service bundle from the application source code.
- **test**: Scripts and configuration files used for testing.
### Files
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **changeLog**: Change highlights associated with official releases.
- **CODE_OF_CONDUCT.md**: Outlines the expected behavior and guidelines for participants within the project's community. 
- **CONTRIBUTING.md**: Overview of the repository, setup instructions, and basic usage examples.
- **Dockerfile**: File used to create a Docker image for the deployment tool.
- **LICENSE**: License information for the repository.
- **pyproject.toml**: Configuration file necessary for building role images.
- **README.md**: Overview of the repository, setup instructions, and basic usage examples.


## Getting Started
To get started with the COLMENA programming model, follow these steps:

1. Clone the Repository:
    ```bash
    git clone https://github.com/colmena-swarm/programming-model.git .
    ```
2. Install Dependencies:
    ```bash
    python3 -m pip install .
    ```

3. Create a sample application:

    To do so, create a Python file with the application code.
    The file should contain at least two classes, the service class and the context class. You can find an example in *test/examples/example_application.py*.

    **Service class**

    The service class extends Service, and contains one inner class per role.
    For example, in example_application.py there are two roles:
    ```python
    class ExampleApplication(Service):
        # ...

        class Sensing(Role):
            # ...

        class Processing(Role):
            # ...
    ```
    The init function of the Service class is annotated with different elements: abstractions to be used by the roles (@Channel, @Metric), KPIS for the QoS evaluation (@KPI), and the context (@Context).
    To continue with the example:
    ```python
    class ExampleApplication(Service):

        @Context(class_ref=CompanyPremises, name="company_premises")
        @Channel(name="buffer", scope=" ")
        @Channel(name="result", scope=" ")
        @Metric(name="sensed")
        @Metric(name="processed")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    ```
    Finally, the init functions of the roles are also annotated with the abstractions and role KPIs.
    ```python
    class Processing(Role):

        @Channel(name="result")
        @Channel(name="buffer")
        @Metric(name="processed")
        @Requirements("CPU")
        @KPI("buffer_queue_size[100000000s] < 10")
        def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    ```
    Note that the abstractions must be first initialized by decorating the service class and then specified in all the roles that will use them:

    Each role has a behavior function, which can be annotated with `@Persistent` or `@Async`:
    ```python
    @Async(image="buffer")
        def behavior(self, image):
    ```
    If it's asynchronous, the function will be called when there are new elements in the channel (and these will be passed as parameters). The persistent functions will be executed continuously.


    **Context class**

    The context class must contain an attribute *structure* specifying the hierarchy of the context, and a function *locate* that returns the agent's position depending on the device's parameters.
    ```python
    class CompanyPremises(Context):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.structure = {
                "floor1": ["reception"],
                "floor2": ["reception", "open_space"],
                "floor3": ["open_space", "manager_office"],
            }

        def locate(self, device):
            print(self.structure["floor1"][0])
    ```

4. Build the service:
    ``` bash
    colmena_build --service_path="<path_to_the_service_root>" \
    ```
    The outcome of the building process will be left at <path_to_the_service_root>/<service_modulename>/build.

### Docker
Alternatively, the service can also be created using docker:
1. Create the corresponding docker image locally
	```bash
	docker --debug build -t colmenaswarm/programming-model:latest .
	```
2. Execute the image mounting as a volume the folder containing the code of service.
	```bash
	docker run --rm \
		-v <path-to-application>:/app \
		colmenaswarm/programming-model:latest \
		--service_path=<path_to_the_service_root>
	```

## Testing

The folder tests/ contains example applications and a series of python tests (test_examples.py) to verify the correct behavior.
To run all tests, execute the following commands on a terminal:
```bash
cd test
python3 -m pytest test_examples.py
```
The tests will make sure that all the files and folders are created properly (test_build_files), that the roles of each service execute without errors (test_roles_in_services), and that the build command runs (test_build).

For adding a new test/example, include the code of the service in the folder and also the reference service model JSON file to compare with. Bear in mind to include it as part of the testing script in order to execute it automatically.

## Contributing
Please read our [contribution guidelines](CONTRIBUTING.md) before making a pull request.

## License
The COLMENA programming model is released under the Apache 2.0 license.
Copyright © 2022-2024 Barcelona Supercomputing Center - Centro Nacional de Supercomputación. All rights reserved.
See the [LICENSE](LICENSE) file for more information.


<sub>
	This work is co-financed by the COLMENA project of the UNICO I+D Cloud program that has the Ministry for Digital Transformation and of Civil Service and the EU-Next Generation EU as financing entities, within the framework of the PRTR and the MRR. It has also been supported by the Spanish Government (PID2019-107255GB-C21), MCIN/AEI /10.13039/501100011033 (CEX2021-001148-S), and Generalitat de Catalunya (2021-SGR-00412).
</sub>
<p align="center">
	<img src="https://github.com/colmena-swarm/.github/blob/assets/images/funding_logos/Logos_entidades_OK.png?raw=true" width="600">
</p>
