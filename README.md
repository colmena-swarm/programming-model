# COLMENA Programming Model Repository

This GitHub repository contains all the files and software necessary to create applications to be deployed on a COLMENA platform. COLMENA (COLaboración entre dispositivos Mediante tecnología de ENjAmbre) aims to ease the development, deployment, operation and maintenance of extremely-high available, reliable and intelligent services running seamlessly across the device-edge-cloud continuum. It leverages a swarm approach organising a dynamic group of autonomous, collaborative nodes following an agile, fully-decentralised, robust, secure and trustworthy open architecture.

## Table of Contents
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)



## Repository Structure
The repository is organized into the following directories and files:

### Directories
- **colmena**: Source code necessary to bundle a COLMENA-compatible service code.
- **scripts**: Scripts to launch the conversion.
### Files
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **CODE_OF_CONDUCT.md**: Outlines the expected behavior and guidelines for participants within the project's community. 
- **CONTRIBUTING.md**: Overview of the repository, setup instructions, and basic usage examples.
- **Dockerfile**: File used to create a Docker image for the deployment tool.
- **LICENSE**: License information for the repository.
- **pyproject.toml**: Configuration file necessary for building role images.
- **README.md**: Overview of the repository, setup instructions, and basic usage examples.



## Getting Started
For building a service using the programming model run the colmena_build command.
``` bash
python3 -m colmena_build \
	--colmena_path="<this_repository_root>" \
	--service_code_path="<path_to_the_service_root>" \
	--module_name="<service_modulename>" \
	--service_name="<service_classname>" 
```
The outcome of the building process will be left at <path_to_the_service_root>/<service_modulename>/build.

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
		--module_name=<service_modulename> \
		--service_name=<service_classname>
	```
	

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
