import trafilatura
import streamlit as st
import requests

def extract_content_from_urls(urls):
    """
    Extracts main content from a list of URLs using trafilatura.
    Returns a list of dictionaries with 'url' and 'markdown_content'.
    """
    extracted_articles = []
    for url in urls:
        try:
            st.info(f"Extracting content from: {url}")
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # trafilatura.extract returns markdown by default if output_format='markdown'
                # or plain text if output_format='text'
                # For simplicity, let's aim for plain text or markdown directly from extract
                extracted_text = trafilatura.extract(downloaded, output_format='markdown', include_links=True, include_images=False)
                if extracted_text:
                    extracted_articles.append({
                        "url": url,
                        "markdown_content": extracted_text
                    })
                else:
                    st.warning(f"Could not extract content from {url}. Skipping.")
            else:
                st.warning(f"Failed to download content from {url}. Skipping.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error while fetching {url}: {e}")
        except Exception as e:
            st.error(f"Error extracting content from {url}: {e}")
    return extracted_articles