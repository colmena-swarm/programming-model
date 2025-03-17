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

FROM python:3.9.18-slim-bookworm

    ARG BUILD_DATE=2025-08-18

    LABEL org.label-schema.name="Colmena's Programming Model" \
          org.label-schema.description="Tool for creating services to be deployed on a COLMENA platform" \
          org.label-schema.build-date="${BUILD_DATE}" \
          org.label-schema.url="http://proyecto-colmena.com" \
          org.label-schema.vcs-url="https://github.com/colmena-swarm/programming-model" \
          maintainer="Barcelona Supercomputing Center"

    COPY . /colmena
    WORKDIR /colmena

    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            git=1:2.39.5-0+deb12u2 && \
        python3 -m pip install --no-cache-dir . && \
        apt-get remove -y git && \
        rm -rf /var/lib/apt/lists/*

    RUN python3 -m pip install --no-cache-dir .[role]

    WORKDIR /colmena/scripts
    ENTRYPOINT ["colmena_build", "--build_file=/colmena/dist/colmena_swarm_pm-0.1.4.tar.gz"]
