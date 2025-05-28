# Task Breakdown for AI Orchestrator: Dockerized Sales Research Assistant

**Project:** Dockerized Sales Research Assistant
**Version:** 1.0
**Reference Document:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md)

**Instructions for AI Orchestrator:**
*   Process tasks sequentially based on `Depends On` field.
*   Update `Status` for each task as it's processed.
*   All file paths are relative to the project root unless specified otherwise.
*   Prioritize simplicity and speed for MVP as per [`PROJECT_PLAN.md`](PROJECT_PLAN.md).
*   Credentials (Google Client ID/Secret, Gemini API Key) will be provided as environment variables at runtime, do not hardcode. Placeholder values can be used during development if actuals are not yet available, clearly marking them.

---

## Phase 0: Project Setup & Configuration (Manual/External)
*These tasks are typically performed manually or outside the direct coding scope of the AI agent but are listed for completeness and context.*

**Task ID:** 0.1 - Create Google Cloud Project
*   **Status:** PENDING (Manual)
*   **Depends On:** None
*   **Description:** Set up a new Google Cloud Project.
*   **Inputs:** N/A
*   **Outputs/Deliverables:** Google Cloud Project ID.
*   **AI Agent Instructions/Notes:** This is a manual step. The Project ID will be needed for subsequent API configurations.

**Task ID:** 0.2 - Enable APIs
*   **Status:** PENDING (Manual)
*   **Depends On:** 0.1
*   **Description:** Enable Gemini API and Google Drive API in the Google Cloud Project.
*   **Inputs:** Google Cloud Project ID.
*   **Outputs/Deliverables:** APIs enabled status.
*   **AI Agent Instructions/Notes:** Manual step.

**Task ID:** 0.3 - Create OAuth 2.0 Credentials
*   **Status:** PENDING (Manual)
*   **Depends On:** 0.2
*   **Description:** Create OAuth 2.0 Credentials (Client ID, Client Secret) for a "Web application." Configure redirect URIs (e.g., `http://localhost:8501/callback`, `http://localhost:PORT/auth/callback` or similar for Streamlit/Flask).
*   **Inputs:** Google Cloud Project ID.
*   **Outputs/Deliverables:**
    *   `GOOGLE_CLIENT_ID`
    *   `GOOGLE_CLIENT_SECRET`
    *   Configured Redirect URI(s)
*   **AI Agent Instructions/Notes:** Manual step. These credentials will be used as environment variables.

**Task ID:** 0.4 - Obtain Gemini API Key
*   **Status:** PENDING (Manual)
*   **Depends On:** 0.2
*   **Description:** Obtain an API Key for the Gemini API from the Google Cloud Project.
*   **Inputs:** Google Cloud Project ID.
*   **Outputs/Deliverables:** `GEMINI_API_KEY`.
*   **AI Agent Instructions/Notes:** Manual step. This key will be used as an environment variable.

**Task ID:** 0.5 - Initialize Project Directory Structure
*   **Status:** COMPLETED
*   **Depends On:** None
*   **Description:** Create the basic directory structure for the project.
    ```
    sales_research_app/
    ├── app.py               # Main Streamlit application
    ├── modules/             # Directory for backend Python modules
    │   ├── __init__.py
    │   ├── auth.py          # Google OAuth logic
    │   ├── gemini.py        # Gemini API interaction
    │   ├── extractor.py     # Content extraction
    │   ├── gdrive.py        # Google Drive interaction
    ├── requirements.txt     # Python dependencies
    ├── Dockerfile
    ├── .env.example         # Example environment variables
    ├── static/              # Optional: for CSS/JS if extending Streamlit
    └── README.md
    ```
*   **Inputs:** None
*   **Outputs/Deliverables:** Created directory structure and empty placeholder files (e.g., `__init__.py` in modules).
*   **AI Agent Instructions/Notes:** Create the directories and the specified empty files or files with minimal boilerplate if appropriate (e.g., `__init__.py`). `app.py` can be empty for now.

---

## Phase 1: Core Backend Logic

**Task ID:** 1.1.1 - Implement Google OAuth 2.0 Flow (auth.py)
*   **Status:** COMPLETED
*   **Depends On:** 0.5
*   **Description:** Implement the server-side logic for Google OAuth 2.0 authentication using `google-auth-oauthlib` and `google-api-python-client`. This module will handle the redirect to Google, callback processing, and token exchange. Store tokens in Streamlit's session state.
*   **Inputs:**
    *   `GOOGLE_CLIENT_ID` (from env var)
    *   `GOOGLE_CLIENT_SECRET` (from env var)
    *   Redirect URI (e.g., `http://localhost:8501/callback` or as defined for Streamlit)
    *   Scopes: `['https://www.googleapis.com/auth/drive.file', 'openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']`
*   **Outputs/Deliverables:**
    *   [`modules/auth.py`](modules/auth.py) containing:
        *   Function to build the authorization URL.
        *   Function to fetch tokens from the authorization code (callback handler).
        *   Function to get authorized Google API service client (e.g., for Drive) or credentials object.
        *   Function to get user profile info (email, name).
*   **AI Agent Instructions/Notes:**
    *   Focus on Streamlit integration for session state (`st.session_state`).
    *   The redirect URI for Streamlit might not be a direct callback URL in the same way as Flask/Django. Often, Streamlit apps handle this by checking query parameters on the main app URL after redirect. Research best practices for Streamlit OAuth. For simplicity, the callback logic might be part of the main `app.py` initially, calling functions from `auth.py`.
    *   Ensure secure handling of client secrets.
    *   Provide functions to check if user is authenticated and to retrieve credentials from session.

**Task ID:** 1.2.1 - Implement Gemini Interaction Module (gemini.py)
*   **Status:** COMPLETED
*   **Depends On:** 0.5
*   **Description:** Create a module to interact with the Google Gemini API using the `google-generativeai` library.
*   **Inputs:**
    *   `GEMINI_API_KEY` (from env var)
    *   Company Name (string)
*   **Outputs/Deliverables:**
    *   [`modules/gemini.py`](modules/gemini.py) containing:
        *   Function `research_company(company_name)` that takes a company name.
        *   This function should construct prompts for:
            1.  Company overview.
            2.  Key competitors.
            3.  Relevant news/articles (requesting source URLs).
        *   Makes API calls to Gemini for each prompt.
        *   Parses responses to extract text and source URLs.
        *   Returns a structured dictionary, e.g., `{"overview": "...", "competitors": ["...", "..."], "articles": [{"title": "...", "url": "..."}]}`.
*   **AI Agent Instructions/Notes:**
    *   Initialize the Gemini client using the API key.
    *   Craft prompts carefully to elicit desired information and source URLs.
    *   Implement basic error handling for API calls.
    *   Keep prompts simple for MVP.

**Task ID:** 1.3.1 - Implement Content Extraction Module (extractor.py)
*   **Status:** COMPLETED
*   **Depends On:** 0.5
*   **Description:** Create a module to extract main content from URLs using the `trafilatura` library.
*   **Inputs:**
    *   List of URLs (strings)
*   **Outputs/Deliverables:**
    *   [`modules/extractor.py`](modules/extractor.py) containing:
        *   Function `extract_content_from_urls(urls)` that takes a list of URLs.
        *   For each URL, fetches and extracts the main text content.
        *   Converts extracted content to Markdown format (trafilatura can output text; ensure it's suitable or use `markdownify` if HTML is involved and needs conversion).
        *   Returns a list of dictionaries, e.g., `[{"url": "...", "markdown_content": "..."}, ...]`.
*   **AI Agent Instructions/Notes:**
    *   Handle potential errors during fetching or extraction (e.g., network issues, non-HTML content).
    *   `trafilatura.extract(downloaded_page_content)` is a key function.
    *   Ensure output is plain text Markdown.

**Task ID:** 1.4.1 - Implement Google Drive Integration Module (gdrive.py)
*   **Status:** COMPLETED
*   **Depends On:** 1.1.1 (for authenticated credentials/service object)
*   **Description:** Create a module to interact with Google Drive API: create folders and upload files.
*   **Inputs:**
    *   Authenticated Google API service client for Drive (from `auth.py` via session state).
    *   Company Name (string, for folder naming).
    *   Research data (e.g., dictionary from Gemini, list of Markdown contents from extractor).
*   **Outputs/Deliverables:**
    *   [`modules/gdrive.py`](modules/gdrive.py) containing:
        *   Function `get_or_create_folder(service, folder_name, parent_id=None)`: Checks if a folder exists, creates if not, returns folder ID.
        *   Function `upload_text_file(service, folder_id, file_name, content, mime_type='text/plain')`: Uploads text content as a file.
        *   Function `save_research_to_drive(service, company_name, research_results, extracted_articles)`:
            1.  Gets/creates a root "Sales Research" folder.
            2.  Creates a subfolder named after `company_name` (e.g., `Company_Name_YYYYMMDDHHMM` for uniqueness if preferred for MVP).
            3.  Saves Gemini research (overview, competitors) as text files (e.g., `overview.txt`, `competitors.txt`).
            4.  Saves extracted Markdown articles as `.md` files in the company subfolder.
            5.  Returns the URL/link to the created company-specific folder.
*   **AI Agent Instructions/Notes:**
    *   Use the `google-api-python-client` for Drive interactions.
    *   Handle permissions and API errors gracefully.
    *   For MVP, if a folder with the exact company name exists, creating a new one or overwriting is acceptable. A timestamped folder name is a simple way to ensure uniqueness: `f"{company_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"`.

---

## Phase 2: Streamlit Application Development

**Task ID:** 2.1.1 - Basic UI Layout (app.py)
*   **Status:** COMPLETED
*   **Depends On:** 0.5
*   **Description:** Create the initial Streamlit UI layout in [`app.py`](app.py).
*   **Inputs:** None
*   **Outputs/Deliverables:**
    *   Modified [`app.py`](app.py) with:
        *   Title: "Sales Research Assistant".
        *   Input field for "Company Name" (`st.text_input`).
        *   "Start Research" button (`st.button`).
        *   Placeholder for Google Sign-In button/status (`st.empty()` or conditional display).
        *   Placeholder for status messages (`st.info` or `st.empty()`).
        *   Placeholder for Google Drive result link (`st.markdown` or `st.link_button`).
*   **AI Agent Instructions/Notes:**
    *   Keep the UI extremely simple.
    *   Use Streamlit's native components.
    *   No backend logic connection in this step, just layout.

**Task ID:** 2.2.1 - Integrate Google Sign-In into UI (app.py)
*   **Status:** COMPLETED
*   **Depends On:** 1.1.1, 2.1.1
*   **Description:** Connect the Google Sign-In flow from [`modules/auth.py`](modules/auth.py) to the Streamlit UI.
*   **Inputs:**
    *   Functions from [`modules/auth.py`](modules/auth.py).
*   **Outputs/Deliverables:**
    *   Modified [`app.py`](app.py):
        *   If user not authenticated: Display "Sign in with Google" button. Clicking it should redirect to Google's auth URL (obtained from `auth.build_authorization_url()`).
        *   Handle the callback: After user authenticates and Google redirects back, `app.py` should capture the `code` from query parameters.
        *   Call `auth.fetch_tokens(code)` to get tokens and store them in `st.session_state.credentials`.
        *   Store user profile (email) in `st.session_state.user_email`.
        *   If authenticated: Display "Signed in as [user_email]" and a "Sign Out" button. Sign out should clear relevant session state.
*   **AI Agent Instructions/Notes:**
    *   Streamlit handles query parameters via `st.experimental_get_query_params()`.
    *   The "Sign in" button might be a `st.link_button` to the auth URL.
    *   State management (`st.session_state`) is key here.
    *   Redirect URI for Streamlit: The app itself is the redirect URI. The callback logic runs when the app reloads with `code` in query params.

**Task ID:** 2.3.1 - Connect UI to Backend Logic (app.py)
*   **Status:** COMPLETED
*   **Depends On:** 1.2.1, 1.3.1, 1.4.1, 2.2.1
*   **Description:** Wire the "Start Research" button to trigger the full research pipeline.
*   **Inputs:**
    *   Company Name from UI.
    *   Authenticated user credentials from `st.session_state`.
    *   Functions from [`modules/gemini.py`](modules/gemini.py), [`modules/extractor.py`](modules/extractor.py), [`modules/gdrive.py`](modules/gdrive.py).
*   **Outputs/Deliverables:**
    *   Modified [`app.py`](app.py):
        *   When "Start Research" is clicked (and user is authenticated):
            1.  Get company name from input.
            2.  Display initial "Processing..." message.
            3.  Call `gemini.research_company(company_name)`. Update status.
            4.  If articles found, call `extractor.extract_content_from_urls(article_urls)`. Update status.
            5.  Call `gdrive.save_research_to_drive(...)` using credentials from session state. Update status.
            6.  Display the returned Google Drive folder link.
*   **AI Agent Instructions/Notes:**
    *   Ensure the Drive service object is created using credentials from `st.session_state.credentials`.
    *   Implement sequential calls and update UI status messages at each step.
    *   Disable "Start Research" button during processing (`disabled` argument in `st.button` and manage via session state).

**Task ID:** 2.4.1 - Implement User Feedback & Progress Display (app.py)
*   **Status:** COMPLETED
*   **Depends On:** 2.3.1
*   **Description:** Enhance UI feedback during processing.
*   **Inputs:** N/A (modifies existing UI flow)
*   **Outputs/Deliverables:**
    *   Modified [`app.py`](app.py) with:
        *   Clear, dynamic status messages (e.g., "Asking Gemini about company overview...", "Extracting content for X articles...", "Uploading to Google Drive..."). Use `st.info()`, `st.success()`, `st.warning()`, `st.error()`.
        *   Loading indicator (e.g., `st.spinner("Processing...")`).
        *   "Start Research" button disabled while processing.
*   **AI Agent Instructions/Notes:** This is largely about refining the user experience within the logic developed in 2.3.1.

**Task ID:** 2.5.1 - Implement Basic Error Handling (app.py and modules)
*   **Status:** COMPLETED
*   **Depends On:** 2.4.1
*   **Description:** Add user-friendly error handling throughout the application.
*   **Inputs:** N/A
*   **Outputs/Deliverables:**
    *   Modified [`app.py`](app.py) and Python modules:
        *   Wrap API calls (Gemini, Drive, content extraction) in try-except blocks.
        *   Catch common exceptions (network errors, API errors, permission issues).
        *   Display clear, non-technical error messages to the user in Streamlit UI (e.g., "Failed to contact Gemini. Please try again.", "Could not save to Google Drive. Ensure permissions are granted.").
*   **AI Agent Instructions/Notes:**
    *   Avoid showing raw stack traces to the user.
    *   Log detailed errors to console for debugging, but show simple messages in UI.

---

## Phase 3: Dockerization

**Task ID:** 3.1.1 - Create requirements.txt
*   **Status:** COMPLETED
*   **Depends On:** 1.1.1, 1.2.1, 1.3.1, 1.4.1
*   **Description:** Generate a `requirements.txt` file listing all Python dependencies.
*   **Inputs:** List of used Python libraries (streamlit, google-auth, google-auth-oauthlib, google-api-python-client, google-generativeai, trafilatura, markdownify).
*   **Outputs/Deliverables:**
    *   [`requirements.txt`](requirements.txt) file.
*   **AI Agent Instructions/Notes:**
    *   Include specific versions if known to be stable, otherwise, let pip resolve latest compatible.
    *   Example content:
        ```
        streamlit
        google-auth
        google-auth-oauthlib
        google-api-python-client
        google-generativeai
        trafilatura
        markdownify
        ```

**Task ID:** 3.2.1 - Write Dockerfile
*   **Status:** COMPLETED
*   **Depends On:** 0.5, 3.1.1
*   **Description:** Create the `Dockerfile` to containerize the Streamlit application.
*   **Inputs:**
    *   Project file structure.
    *   [`requirements.txt`](requirements.txt).
*   **Outputs/Deliverables:**
    *   [`Dockerfile`](Dockerfile)
*   **AI Agent Instructions/Notes:**
    *   Use an official Python base image (e.g., `python:3.9-slim`).
    *   Set up working directory, copy application files.
    *   Install dependencies from `requirements.txt`.
    *   Expose Streamlit port (default 8501).
    *   Set `CMD ["streamlit", "run", "app.py"]`.
    *   Do NOT bake API keys/secrets into the image. These will be passed as environment variables.

**Task ID:** 3.3.1 - Create .env.example
*   **Status:** COMPLETED
*   **Depends On:** 0.3, 0.4
*   **Description:** Create an example environment file.
*   **Inputs:** List of required environment variables.
*   **Outputs/Deliverables:**
    *   `.env.example` file.
*   **AI Agent Instructions/Notes:**
    *   Example content:
        ```
        GOOGLE_CLIENT_ID="YOUR_GOOGLE_CLIENT_ID_HERE"
        GOOGLE_CLIENT_SECRET="YOUR_GOOGLE_CLIENT_SECRET_HERE"
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        # Optional: Set a fixed redirect URI if needed for consistency, though auth.py might construct it dynamically
        # REDIRECT_URI="http://localhost:8501"
        ```

---
## Phase 4: Security & Configuration (Review)

**Task ID:** 4.1.1 - Review Credential Handling
*   **Status:** COMPLETED
*   **Depends On:** 3.2.1, 3.3.1
*   **Description:** Review all code to ensure API keys and secrets are loaded from environment variables and not hardcoded.
*   **Inputs:** All source code files.
*   **Outputs/Deliverables:** Confirmation of secure credential handling.
*   **AI Agent Instructions/Notes:** This is a verification step. Ensure `os.getenv()` or similar is used for all sensitive credentials.

---
## Phase 5: Documentation (Finalization)

**Task ID:** 5.1.1 - Create README.md
*   **Status:** COMPLETED
*   **Depends On:** 3.2.1, 3.3.1
*   **Description:** Create a `README.md` with setup, configuration (env vars), and usage instructions.
*   **Inputs:** Project structure, Dockerfile, .env.example.
*   **Outputs/Deliverables:**
    *   [`README.md`](README.md)
*   **AI Agent Instructions/Notes:**
    *   Include:
        *   Project description.
        *   Prerequisites (Docker, Google Cloud setup).
        *   How to configure environment variables (copy `.env.example` to `.env`).
        *   How to build and run the Docker container.
        *   How to access the application.

---
This detailed breakdown should provide the AI orchestrator with clear, actionable steps to implement the project.