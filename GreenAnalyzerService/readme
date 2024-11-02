# GreenAnalyzerService

## Overview
GreenAnalyzerService is the main component of the GreenAnalyzer Project aimed at serving GreenAnalyzer's API and execute the automated ML pipelines. 
This service includes database integration, a Docker setup, and script-driven management.

## Service Components and Structure
- **docker-compose.yaml**: Docker Compose configuration for containerized deployment.
- **dockerfile**: Defines the Docker image for the service.
- **entrypoint.sh**: Shell script for setting up the environment at container start.
- **manage.py**: Django management script for running the application and administrative tasks.
- **requirements.txt**: List of dependencies required to run the project.

## Installation

### Requirements
- Docker
- Python 3.x
- Recommended: Virtual environment for dependency management

### Setup with Docker

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/UCY-LINC-LAB/GreenAnalyzer-Project.git
   cd GreenAnalyzerService
   ```

2. In order to execute the project via docker, one needs only to run the docker-compose file.

  **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

### Setup locally
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/UCY-LINC-LAB/GreenAnalyzer-Project.git
   cd GreenAnalyzerService
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Locally**:
   ```bash
   python manage.py runserver
   ```

## Usage
To start the application, either run it locally or in Docker. The default configuration uses PostgreSQL, but this can be adapted for other databases by modifying `settings.py`.

## Contributing
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request with detailed information about your contribution.
