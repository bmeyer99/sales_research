import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pickle

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def get_google_auth_flow(redirect_uri):
    """Initializes and returns the Google OAuth 2.0 flow."""
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": "sales-research-app", # Placeholder, not strictly used by flow but good practice
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [redirect_uri]
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def build_authorization_url(redirect_uri):
    """Builds the Google authorization URL."""
    flow = get_google_auth_flow(redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    st.session_state['oauth_state'] = state
    return authorization_url

def fetch_tokens(authorization_response):
    """Fetches tokens from the authorization response."""
    flow = get_google_auth_flow(st.session_state.get('redirect_uri'))
    flow.fetch_token(authorization_response=authorization_response)
    st.session_state['credentials'] = flow.credentials
    return flow.credentials

def get_credentials():
    """Retrieves credentials from session state."""
    if 'credentials' in st.session_state:
        creds = st.session_state['credentials']
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state['credentials'] = creds # Update session state with refreshed creds
        return creds
    return None

def get_user_info(credentials):
    """Fetches user information (email, name) using the credentials."""
    from googleapiclient.discovery import build
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info
    except Exception as e:
        st.error(f"Error fetching user info: {e}")
        return None

def is_authenticated():
    """Checks if the user is authenticated."""
    return 'credentials' in st.session_state and st.session_state['credentials'] is not None

def sign_out():
    """Clears authentication credentials from session state."""
    if 'credentials' in st.session_state:
        del st.session_state['credentials']
    if 'user_info' in st.session_state:
        del st.session_state['user_info']
    if 'oauth_state' in st.session_state:
        del st.session_state['oauth_state']
    if 'redirect_uri' in st.session_state:
        del st.session_state['redirect_uri']