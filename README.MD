JIRA Prometheus Exporter
=============

Overview
--------

This project integrates Prometheus monitoring with a Python application to track and export metrics from JIRA. It utilizes a Docker container for easy deployment and isolation of the environment.

Features
--------

-   JIRA Integration: Interacts with the JIRA API to fetch and process data.
-   Prometheus Metrics Exporter: Exports custom metrics (e.g., issue counts by company) for Prometheus monitoring.
-   Dockerized Application: Containerized for straightforward deployment and scalability.

Getting Started
---------------

### Prerequisites

-   Docker
-   Access to a JIRA instance with necessary permissions

### Installation

1.  Clone the repository.
2.  Ensure Docker is installed and running on your system.

### Configuration

-   Configure the JIRA API credentials and desired metrics in `jira_api.py`.
-   Set up Prometheus to scrape metrics from the application as defined in `example_prometheus.yml`.

### Running the Application

1.  Build the Docker image using the provided Dockerfile.

    arduinoCopy code

    `docker build -t your-image-name .`

2.  Run the Docker container.

    arduinoCopy code

    `docker run -p 8000:8000 your-image-name`

Usage
-----

-   The application will start exporting metrics to Prometheus, as configured.
-   Access the metrics at `http://localhost:8000/`.

Contributing
------------

Contributions are welcome. Please follow the standard pull request process for your contributions.

License
-------

[Your preferred License]