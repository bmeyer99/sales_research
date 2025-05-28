# Sales Research Assistant

## Project Description

The Sales Research Assistant is a Dockerized web application designed to empower sales teams by automating company research. It uses Google Gemini for research and Google Drive for storing the findings. Users can input a company name, and the application will:

1.  Authenticate the user via Google Sign-In.
2.  Use Google Gemini to gather information about the company (overview, competitors, relevant articles).
3.  Extract content from the source URLs provided by Gemini.
4.  Save the research results (Gemini output and extracted content as Markdown) to the user's Google Drive in an organized folder structure.

The application is built with Python and Streamlit for a simple and fast user interface.

## Prerequisites

*   **Docker:** Ensure Docker is installed and running on your system. ([Install Docker](https://docs.docker.com/get-docker/))
*   **Google Cloud Project:**
    *   A Google Cloud Platform (GCP) project.
    *   Gemini API enabled.
    *   Google Drive API enabled.
    *   OAuth 2.0 Credentials (Client ID and Client Secret) for a "Web application."
        *   The **Authorized redirect URIs** for the OAuth 2.0 client ID must include the URL where your Streamlit application will be accessible.
            *   For local development, this is typically `http://localhost:8501`.
            *   For deployment, this will be your application's public URL (e.g., `https://your-app-domain.com`).
    *   A Gemini API Key.

## Configuration

1.  **Clone the repository (if applicable) or ensure you have the `sales_research_app` directory.**
2.  **Navigate to the `sales_research_app` directory:**
    ```bash
    cd path/to/sales_research_app
    ```
3.  **Create an environment file:**
    Copy the example environment file `.env.example` to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
4.  **Edit the `.env` file:**
    Open the `.env` file and replace the placeholder values with your actual Google Cloud credentials:
    ```env
    GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID_HERE"
    GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET_HERE"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    # Optional: Set a fixed redirect URI if needed, otherwise it defaults to http://localhost:8501
    # REDIRECT_URI="http://localhost:8501"
    ```
    *   Ensure `REDIRECT_URI` in your `.env` file (if you set it) or the default used in `modules/auth.py` matches one of the Authorized redirect URIs configured in your Google Cloud OAuth 2.0 client settings.

## How to Build and Run

1.  **Build the Docker image:**
    From within the `sales_research_app` directory, run:
    ```bash
    docker build -t sales-research-assistant .
    ```
2.  **Run the Docker container:**
    Use the environment variables from your `.env` file when running the container:
    ```bash
    docker run -p 8501:8501 --env-file .env sales-research-assistant
    ```
    *   This command maps port 8501 of the container to port 8501 on your host machine.
    *   The `--env-file .env` flag loads your credentials into the container.

## How to Access the Application

Once the Docker container is running:

1.  Open your web browser.
2.  Navigate to `http://localhost:8501`.

You should see the Sales Research Assistant application. Follow the on-screen instructions to sign in with Google and start your research.