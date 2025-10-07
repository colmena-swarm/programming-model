# Stage 1: Build COMPSs Python bindings
FROM {{BASE_IMAGE}} AS compss-builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        build-essential \
        gfortran \
        python3-dev \
        python3-setuptools \
        openjdk-17-jdk-headless \
        maven \
        libtool \
        automake \
        autoconf && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Copy COMPSs framework from submodule
WORKDIR /build
COPY compss /build/compss

# Generate data type enums first
WORKDIR /build/compss/compss/programming_model/bindings
RUN python3 generate_datatype_enums.py

# Build and install bindings-common
WORKDIR /build/compss/compss/programming_model/bindings/bindings-common
RUN mkdir -p /opt/COMPSs/Bindings/bindings-common && \
    ./install_common "/opt/COMPSs/Bindings/bindings-common"

# Build and install Python bindings
WORKDIR /build/compss
RUN mkdir -p /opt/COMPSs/Bindings/python && \
    ./compss/programming_model/bindings/python/install.sh "/opt/COMPSs/Bindings/python" true python3

# Copy runtime scripts
RUN mkdir -p /opt/COMPSs/Runtime/scripts && \
    cp -r /build/compss/compss/runtime/scripts/* /opt/COMPSs/Runtime/scripts/

# Stage 2: Final runtime image
FROM {{BASE_IMAGE}}

# Copy COMPSs bindings-common library from builder stage
COPY --from=compss-builder /opt/COMPSs/Bindings/bindings-common /app/Bindings/bindings-common

# Copy COMPSs Python bindings from builder stage
COPY --from=compss-builder /opt/COMPSs/Bindings/python /app/Bindings/python

# Copy COMPSs runtime scripts from builder stage
COPY --from=compss-builder /opt/COMPSs/Runtime/scripts /app/Runtime/scripts

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-venv \
        build-essential \
        gfortran \
        python3-numpy \
        openjdk-17-jre-headless \
        uuid-runtime && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Create venv and install Python dependencies at build time
RUN python3 -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install -r /app/requirements.txt

# Copy the rest of the application
COPY . /app

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/Runtime/scripts/user/runcompss", \
    "--debug", \
    "--tracing=false", \
    "--socket=/tmp/compss.sock", \
    "/app/{{PACKAGE_NAME}}/main.py"]
