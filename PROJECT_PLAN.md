# Project Plan: Dockerized Sales Research Assistant

**Version:** 1.0
**Date:** 2025-05-28
**Architect:** Archer

## 1. Overview

This project aims to create a Dockerized web application to empower the sales team by automating company research using Google Gemini and saving findings to Google Drive. The application will feature a simple UI for inputting a company name, Google Sign-In for user authentication and Drive access, and display progress updates. The primary goal is rapid development and deployment of a functional MVP.

## 2. Goals

*   Develop a web application with a minimal, user-friendly interface.
*   Integrate Google Sign-In for user authentication and authorization for Google Drive.
*   Utilize Google Gemini API for company research (overview, competitors).
*   Extract content from source URLs provided by Gemini.
*   Save research results (Gemini output, extracted content as Markdown) to the user's Google Drive in an organized manner.
*   Package the application as a Docker container for portability and ease of deployment.
*   Prioritize speed of development and simplicity.
*   Ensure secure handling of credentials and user data.

## 3. Technology Stack

*   **Frontend & Backend Framework:** Streamlit (Python)
    *   *Reasoning:* Rapid UI development, Python-native, good for simple data-centric apps. Backend logic can be integrated directly.
*   **Language:** Python
*   **Google Authentication & API Client:**
    *   `google-auth`
    *   `google-auth-oauthlib`
    *   `google-api-python-client`
    *   *Reasoning:* Official Google libraries for OAuth 2.0 and API interactions.
*   **Gemini API Client:** `google-generativeai`
    *   *Reasoning:* Official Python SDK for Gemini.
*   **Content Extraction:** `trafilatura` (Python library)
    *   *Reasoning:* Effective for extracting main content from web pages, Python-native, simpler than setting up an external service like Mercury Parser for an MVP.
*   **Containerization:** Docker
    *   *Reasoning:* Standard for packaging applications and ensuring consistent environments.
*   **Credential Management:** Environment variables (passed to Docker container at runtime).

## 4. Development Phases & High-Level Tasks

### Phase 0: Project Setup & Configuration
*   0.1. Create Google Cloud Project.
*   0.2. Enable Gemini API and Google Drive API.
*   0.3. Create OAuth 2.0 Credentials (Client ID, Client Secret) for "Web application."
    *   Configure redirect URIs (e.g., `http://localhost:8501/callback` for local Streamlit, and production URL later).
*   0.4. Obtain Gemini API Key.
*   0.5. Initialize project directory structure.
*   0.6. Create `TASK_BREAKDOWN_FOR_AI.md` for detailed task tracking.

### Phase 1: Core Backend Logic (Iterative Python Scripting)
*   1.1. **Google OAuth 2.0 Module:**
    *   Implement Google Sign-In flow (authorization code exchange for tokens).
    *   Securely manage tokens (session-based for simplicity).
*   1.2. **Gemini Interaction Module:**
    *   Function to take company name and research type as input.
    *   Construct prompts for Gemini (company info, competitors, ensure source URL requests).
    *   Make API calls to Gemini.
    *   Parse responses (text and source URLs).
*   1.3. **Content Extraction Module:**
    *   Function to take a list of URLs.
    *   Use `trafilatura` to fetch and extract main content.
    *   Convert extracted content to Markdown (e.g., using `markdownify` if HTML is returned, or ensure `trafilatura` outputs clean text).
*   1.4. **Google Drive Integration Module:**
    *   Function to use authenticated user's credentials.
    *   Check/create root "Sales Research" folder.
    *   Create company-specific subfolder.
    *   Save Gemini reports (text files) and Markdown content to the subfolder.

### Phase 2: Streamlit Application Development
*   2.1. **Basic UI Layout:**
    *   Input field for "Company Name."
    *   "Start Research" button.
    *   Google Sign-In button/area.
    *   Status display area.
    *   Link area for Google Drive results.
*   2.2. **Integrate Google Sign-In:**
    *   Connect UI button to backend OAuth flow.
    *   Handle successful sign-in and token storage in session state.
    *   Display user authentication status.
*   2.3. **Connect UI to Backend Logic:**
    *   On "Start Research" click:
        *   Retrieve company name.
        *   Trigger Gemini research.
        *   Trigger content extraction.
        *   Trigger Google Drive upload.
*   2.4. **User Feedback & Progress Display:**
    *   Disable button during processing.
    *   Show dynamic status messages (e.g., "Researching...", "Extracting...", "Uploading...").
    *   Display final Google Drive link.
*   2.5. **Error Handling:**
    *   User-friendly messages for API errors, network issues, permission denials.

### Phase 3: Dockerization
*   3.1. Create `requirements.txt` listing all Python dependencies.
*   3.2. Write `Dockerfile`:
    *   Base Python image.
    *   Copy application code.
    *   Install dependencies.
    *   Set up working directory.
    *   Define entry point (e.g., `streamlit run app.py`).
*   3.3. Build and test Docker image locally.
*   3.4. (Optional) Create `docker-compose.yml` if needed later for multi-service setups.

### Phase 4: Security & Configuration
*   4.1. Ensure API keys (Gemini) and OAuth client secrets are NOT hardcoded.
*   4.2. Load sensitive credentials from environment variables at runtime in the Docker container.
*   4.3. Review token handling for security.

### Phase 5: Documentation
*   5.1. Create `README.md` with setup, configuration (env vars), and usage instructions.
*   5.2. Finalize `PROJECT_PLAN.md` (this document).
*   5.3. Ensure `TASK_BREAKDOWN_FOR_AI.md` is complete and accurate.

## 5. User Workflow

1.  **Access:** User navigates to the web UI URL.
2.  **Sign-In:** Clicks "Sign in with Google," authenticates, and grants Drive permissions.
3.  **Input:** Enters "Company Name" and clicks "Start Research."
4.  **Processing:** UI shows progress messages.
5.  **Completion:** UI displays "Research complete!" and a link to the Google Drive folder.

## 6. Key Considerations

*   **Stupid-User-Proofing:** Minimal UI, clear instructions, robust error handling, progress feedback.
*   **Idempotency:** For MVP, creating a new folder with a timestamp if one with the exact name exists is acceptable to avoid complexity.
*   **API Quotas & Costs:** Be mindful of Gemini and Drive API limits. Initial version will not have complex quota management.
*   **Modularity:** Design Python modules for reusability and testability.
*   **AI Orchestration:** Structure tasks in `TASK_BREAKDOWN_FOR_AI.md` to be clear and actionable for an AI agent, minimizing ambiguity and the need for follow-up questions for each sub-task.

## 7. Tracking

Progress will be tracked using `TASK_BREAKDOWN_FOR_AI.md`, which will list each specific sub-task, its status, inputs, outputs, and any notes relevant for AI-driven implementation.