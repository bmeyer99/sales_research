import streamlit as st
import os
from modules import auth, gemini, extractor, gdrive
print("DEBUG: App is starting...")

st.set_page_config(page_title="Sales Research Assistant", layout="centered")

# --- Google Authentication Setup & Callback Handling ---
if 'redirect_uri' not in st.session_state:
    st.session_state['redirect_uri'] = os.getenv("REDIRECT_URI", "http://localhost:8501")

# Check for authorization code in query parameters after redirect
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    # Ensure query_params are accessed correctly (they are dict-like, values are lists)
    auth_code = query_params.get("code")[0] if query_params.get("code") else None
    auth_state = query_params.get("state")[0] if query_params.get("state") else None

    if auth_code and auth_state == st.session_state.get('oauth_state'):
        try:
            auth.fetch_tokens(auth_code)
            # Clear query params after successful token fetch to prevent re-processing
            st.query_params.clear()
            # Rerun to reflect authenticated state immediately and remove params from URL
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error during Google sign-in: {e}")
            st.query_params.clear() # Clear params on error too
    elif auth_state and auth_state != st.session_state.get('oauth_state'):
        st.error("OAuth state mismatch. Please try signing in again.")
        st.query_params.clear() # Clear params on state mismatch

# --- Main Application Logic: Conditional display based on authentication ---
if auth.is_authenticated():
    # --- Authenticated View ---
    st.title("Sales Research Assistant")

    credentials = auth.get_credentials() # Get fresh or refreshed credentials
    if 'user_info' not in st.session_state or not st.session_state.get('user_info'): # Fetch if not in session or empty
        if credentials:
            st.session_state['user_info'] = auth.get_user_info(credentials)
        else: # Should not happen if authenticated, but as a safeguard
            auth.sign_out()
            st.experimental_rerun() # Force re-check of authentication

    if st.session_state.get('user_info'):
        st.sidebar.success(f"Signed in as {st.session_state['user_info'].get('email')}")
        if st.sidebar.button("Sign Out", key="sidebar_sign_out_button"):
            auth.sign_out()
            st.experimental_rerun()
    else:
        st.sidebar.warning("Authenticated, but could not retrieve user info.")
        if st.sidebar.button("Sign Out", key="sidebar_sign_out_error_button"):
            auth.sign_out()
            st.experimental_rerun()

    st.markdown("---") # Separator

    # Input for company name
    company_name = st.text_input("Enter Company Name", key="company_name_input")

    # Start Research button - auth check is implicitly handled by being in this block
    start_research_button = st.button("Start Research", key="start_research_button", disabled=not company_name)

    # Placeholders for messages, defined within the authenticated scope
    status_message_placeholder = st.empty()
    drive_link_placeholder = st.empty()

    if start_research_button:
        if not company_name:
            status_message_placeholder.error("Please enter a company name to start research.")
        else:
            status_message_placeholder.info(f"Starting research for {company_name}...")
            
            with st.spinner("Researching company information with Gemini..."):
                research_results = gemini.research_company(company_name)
            
            if research_results:
                status_message_placeholder.success("Gemini research complete!")
                
                article_urls = [article['url'] for article in research_results.get('articles', []) if article.get('url')]
                extracted_articles = []
                if article_urls:
                    with st.spinner("Extracting content from articles..."):
                        extracted_articles = extractor.extract_content_from_urls(article_urls)
                    if extracted_articles: # Check if any articles were successfully extracted
                        status_message_placeholder.success(f"Extracted content from {len(extracted_articles)} articles.")
                    else:
                        status_message_placeholder.info("No content could be extracted from the found articles.")
                else:
                    status_message_placeholder.warning("No articles found by Gemini research.")

                current_credentials = auth.get_credentials() # Re-check credentials before sensitive operations
                if current_credentials:
                    with st.spinner("Saving results to Google Drive..."):
                        drive_link = gdrive.save_research_to_drive(current_credentials, company_name, research_results, extracted_articles)
                        if drive_link:
                            drive_link_placeholder.success("Research complete! Files saved to Google Drive.")
                            drive_link_placeholder.markdown(f"**[View in Google Drive]({drive_link})**")
                        else:
                            status_message_placeholder.error("Failed to save to Google Drive.")
                else:
                    status_message_placeholder.error("Google credentials became invalid. Please sign out and sign in again.")
            else:
                status_message_placeholder.error("Gemini research failed. Please try again.")
else:
    # --- Unauthenticated View ---
    st.title("Sales Research Assistant")
    st.info("To use the Sales Research Assistant, please sign in with your Google account.")
    st.write(f"Configured Redirect URI: `{st.session_state['redirect_uri']}`") # Display on UI
    
    print(f"DEBUG: redirect_uri from st.session_state in app.py: {st.session_state['redirect_uri']}")
    auth_url = auth.build_authorization_url(st.session_state['redirect_uri'])
    st.write(f"DEBUG: oauth_state set before redirect: `{st.session_state.get('oauth_state')}`") # Removed as state is now stored in file
    st.write(f"DEBUG: Full Authorization URL: `{auth_url}`")
    
    button_container = st.container()
    with button_container:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Sign in with Google", key="main_login_button", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={auth_url}">', unsafe_allow_html=True)
                # st.stop() # Removed to prevent session state issues

    st.markdown("---")
    st.caption("This application requires Google authentication to access its features and save research data to your Google Drive.")