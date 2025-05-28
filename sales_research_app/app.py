import streamlit as st
import os
from modules import auth, gemini, extractor, gdrive

st.set_page_config(page_title="Sales Research Assistant", layout="centered")

st.title("Sales Research Assistant")

# Placeholder for authentication status and buttons
auth_status_placeholder = st.empty()
auth_button_placeholder = st.empty()

# --- Google Authentication ---
if 'redirect_uri' not in st.session_state:
    # This needs to be the URL where your Streamlit app is running
    # For local development, it's usually http://localhost:8501
    # For deployment, it will be your app's public URL
    st.session_state['redirect_uri'] = os.getenv("REDIRECT_URI", "http://localhost:8501")

# Check for authorization code in query parameters after redirect
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    if query_params["state"][0] == st.session_state.get('oauth_state'):
        try:
            auth.fetch_tokens(st.query_params.get("code")[0])
            st.query_params.clear() # Clear query params
            st.success("Successfully signed in with Google!")
        except Exception as e:
            st.error(f"Error during Google sign-in: {e}")
    else:
        st.error("OAuth state mismatch. Please try signing in again.")
        st.experimental_set_query_params() # Clear query params

if auth.is_authenticated():
    credentials = auth.get_credentials()
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = auth.get_user_info(credentials)
    
    if st.session_state['user_info']:
        auth_status_placeholder.success(f"Signed in as {st.session_state['user_info'].get('email')}")
        if auth_button_placeholder.button("Sign Out", key="sign_out_button"):
            auth.sign_out()
            st.session_state['user_info'] = None # Clear user info
            st.experimental_rerun()
    else:
        auth_status_placeholder.warning("Could not retrieve user info.")
        if auth_button_placeholder.button("Sign Out", key="sign_out_button_error"):
            auth.sign_out()
            st.experimental_rerun()
else:
    auth_status_placeholder.info("To be able to save the documents into your Google Drive. Please sign in with Google to proceed.")
    auth_url = auth.build_authorization_url(st.session_state['redirect_uri'])
    auth_button_placeholder.link_button("Sign in with Google", auth_url)

st.markdown("---") # Separator

# Input for company name
company_name = st.text_input("Enter Company Name", key="company_name_input")

# Start Research button
start_research_button = st.button("Start Research", key="start_research_button", disabled=not auth.is_authenticated() or not company_name)

# Placeholder for status messages
status_message_placeholder = st.empty()

# Placeholder for Google Drive link
drive_link_placeholder = st.empty()

if start_research_button:
    if not company_name:
        status_message_placeholder.error("Please enter a company name to start research.")
    elif not auth.is_authenticated():
        status_message_placeholder.error("Please sign in with Google first.")
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
                status_message_placeholder.success(f"Extracted content from {len(extracted_articles)} articles.")
            else:
                status_message_placeholder.warning("No articles found or extracted.")

            with st.spinner("Saving results to Google Drive..."):
                credentials = auth.get_credentials()
                if credentials:
                    drive_link = gdrive.save_research_to_drive(credentials, company_name, research_results, extracted_articles)
                    if drive_link:
                        drive_link_placeholder.success("Research complete! Files saved to Google Drive.")
                        drive_link_placeholder.markdown(f"**[View in Google Drive]({drive_link})**")
                    else:
                        status_message_placeholder.error("Failed to save to Google Drive.")
                else:
                    status_message_placeholder.error("Google credentials not found. Please sign in again.")
        else:
            status_message_placeholder.error("Gemini research failed. Please try again.")