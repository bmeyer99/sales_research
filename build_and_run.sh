#!/bin/bash

# Script to check prerequisites, build, and run the Sales Research Assistant Docker container.

# --- Configuration ---
APP_DIR="sales_research_app"
ENV_FILE="${APP_DIR}/.env"
# No longer needed as docker-compose handles naming

# --- Helper Functions ---
print_error() {
  echo -e "\033[0;31mERROR: $1\033[0m"
}

print_success() {
  echo -e "\033[0;32mSUCCESS: $1\033[0m"
}

print_info() {
  echo -e "\033[0;34mINFO: $1\033[0m"
}

# --- Prerequisite Checks ---
print_info "Checking prerequisites..."

# 1. Check for Docker
if ! command -v docker &> /dev/null; then
  print_error "Docker could not be found. Please install Docker. (https://docs.docker.com/get-docker/)"
  exit 1
fi
print_success "Docker is installed."

# 2. Check for Docker Compose
if ! command -v docker compose &> /dev/null; then
  print_error "Docker Compose (v2) could not be found. Please ensure Docker Compose is installed and available via 'docker compose'. (https://docs.docker.com/compose/install/)"
  exit 1
fi
print_success "Docker Compose (v2) is installed."

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi
print_success "Docker daemon is running."

# Check for .env file
if [ ! -f "$ENV_FILE" ]; then
  print_error "$ENV_FILE not found. Please create it by copying from ${APP_DIR}/.env.example and filling in your credentials."
  print_info "See ${APP_DIR}/README.md for details on setting up credentials."
  exit 1
fi
print_success "$ENV_FILE found."

# 3. Check for essential variables in .env file
check_env_var() {
  VAR_NAME=$1
  if ! grep -q "^${VAR_NAME}=" "$ENV_FILE" || [[ -z "$(grep "^${VAR_NAME}=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"')" ]]; then
    print_error "Required environment variable ${VAR_NAME} is not set or is empty in $ENV_FILE."
    print_info "Please ensure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GEMINI_API_KEY are correctly set."
    return 1
  fi
  return 0
}

MISSING_VARS=0
check_env_var "GOOGLE_CLIENT_ID" || MISSING_VARS=1
check_env_var "GOOGLE_CLIENT_SECRET" || MISSING_VARS=1
check_env_var "GEMINI_API_KEY" || MISSING_VARS=1

if [ "$MISSING_VARS" -eq 1 ]; then
  exit 1
fi
print_success "Essential environment variables are present in $ENV_FILE."

# --- Build and Run ---
print_info "All prerequisites met. Proceeding..."

print_info "--- Ensuring no old container is running ---"
# Check if the container exists (running or stopped)
# Use docker-compose to stop and remove existing containers
if docker compose ps -q &> /dev/null; then
    print_info "Stopping and removing existing Docker Compose services..."
    if docker compose down; then
        print_success "Docker Compose services stopped and removed."
    else
        print_error "Failed to stop and remove Docker Compose services. Manual intervention may be required."
        exit 1
    fi
else
    print_info "No existing Docker Compose services found. Good to go."
fi
print_info "--- Old container check complete ---"

# Build and run the Docker container using docker-compose
print_info "Building Docker image with Docker Buildx..."
# The image is tagged as <project_name>_<service_name>:latest, which is sales-trainer_sales-research-app:latest
# The project name 'sales-trainer' is derived from the directory where docker-compose is run.
if docker buildx build --load -t sales-trainer_sales-research-app:latest -f ./sales_research_app/Dockerfile ./sales_research_app; then
    print_success "Docker image 'sales-trainer_sales-research-app:latest' built successfully with Buildx."
else
    print_error "Docker Buildx image build failed."
    exit 1
fi

print_info "Starting Docker containers with docker-compose..."
print_info "Application will be available via Traefik at research.no13productions.com (if configured in docker-compose.yml and Traefik)"
if docker compose up -d; then # --build flag removed
  print_success "Docker Compose services started successfully."
  print_info "To view logs: docker compose logs -f"
  print_info "To stop the services: docker compose down"
else
  print_error "Failed to start Docker Compose services."
  exit 1
fi

print_info "Script finished."