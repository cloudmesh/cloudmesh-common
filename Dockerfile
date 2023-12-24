# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3.12 python3.12-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install additional dependencies
RUN python3.12 -m venv ENV3 && \
    . ENV3/bin/activate && \
    pip install -r requirements.txt

# Specify the default command to run on container start
CMD ["pytest", "tests", "-rsx"]
