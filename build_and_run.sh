#!/bin/bash

# Script to check prerequisites, build, and run the Sales Research Assistant Docker container.

# --- Configuration ---
APP_DIR="sales_research_app"
ENV_FILE="${APP_DIR}/.env"
IMAGE_NAME="sales-research-assistant"
CONTAINER_NAME="sales-research-assistant-container"

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

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi
print_success "Docker daemon is running."


# 2. Check for .env file
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
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    print_info "Found existing container '$CONTAINER_NAME'."
    # Check if it's running
    if [ "$(docker ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
        print_info "Stopping running container '$CONTAINER_NAME'..."
        if docker stop "$CONTAINER_NAME"; then
            print_success "Container '$CONTAINER_NAME' stopped."
        else
            print_error "Failed to stop container '$CONTAINER_NAME'. It might be stuck. Manual intervention may be required. Continuing to attempt removal."
        fi
    fi
    print_info "Removing container '$CONTAINER_NAME'..."
    if docker rm "$CONTAINER_NAME"; then
        print_success "Container '$CONTAINER_NAME' removed."
    else
        print_error "Failed to remove container '$CONTAINER_NAME'. It might have already been removed or is in a problematic state. Continuing..."
    fi
else
    print_info "No existing container named '$CONTAINER_NAME' found. Good to go."
fi
print_info "--- Old container check complete ---"

# Navigate to the app directory
print_info "Navigating to $APP_DIR..."
cd "$APP_DIR" || { print_error "Could not navigate to $APP_DIR directory."; exit 1; }

# Build the Docker image
print_info "Building Docker image '$IMAGE_NAME'..."
if docker build -t "$IMAGE_NAME" .; then
  print_success "Docker image '$IMAGE_NAME' built successfully."
else
  print_error "Docker image build failed."
  cd .. # Navigate back to project root
  exit 1
fi

# Run the Docker container
print_info "Running Docker container '$CONTAINER_NAME' from image '$IMAGE_NAME'..."
print_info "Application will be available at http://localhost:8501"
if docker run -d -p 8501:8501 --env-file .env --name "$CONTAINER_NAME" "$IMAGE_NAME"; then
  print_success "Docker container '$CONTAINER_NAME' started successfully."
  print_info "To view logs: docker logs -f $CONTAINER_NAME"
  print_info "To stop the container: docker stop $CONTAINER_NAME"
else
  print_error "Failed to start Docker container '$CONTAINER_NAME'."
  cd .. # Navigate back to project root
  exit 1
fi

# Navigate back to project root
cd ..
print_info "Script finished."