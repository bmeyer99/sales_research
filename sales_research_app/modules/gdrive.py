import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

def get_or_create_folder(service, folder_name, parent_id=None):
    """
    Checks if a folder exists, creates it if not, and returns its ID.
    """
    try:
        # Search for the folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])

        if files:
            # Folder found
            return files[0]['id']
        else:
            # Folder not found, create it
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = service.files().create(body=file_metadata, fields='id').execute()
            st.success(f"Created Google Drive folder: {folder_name}")
            return folder.get('id')
    except Exception as e:
        st.error(f"Error getting or creating folder '{folder_name}': {e}")
        return None

def upload_text_file(service, folder_id, file_name, content, mime_type='text/plain'):
    """
    Uploads text content as a file to a specified Google Drive folder.
    """
    try:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(
            filename=None, # No local file, content is in memory
            mimetype=mime_type,
            body=content,
            resumable=True
        )
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        st.success(f"Uploaded '{file_name}' to Google Drive.")
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Error uploading file '{file_name}': {e}")
        return None

def save_research_to_drive(credentials, company_name, research_results, extracted_articles):
    """
    Saves research results and extracted articles to Google Drive.
    Returns the URL to the created company-specific folder.
    """
    try:
        service = build('drive', 'v3', credentials=credentials)

        # 1. Get or create root "Sales Research" folder
        root_folder_name = "Sales Research"
        root_folder_id = get_or_create_folder(service, root_folder_name)
        if not root_folder_id:
            return None

        # 2. Create a new subfolder named after the company with a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_folder_name = f"{company_name}_{timestamp}"
        company_folder_id = get_or_create_folder(service, company_folder_name, root_folder_id)
        if not company_folder_id:
            return None

        # 3. Save Gemini research results
        st.info("Saving Gemini research reports...")
        overview_link = upload_text_file(service, company_folder_id, "company_overview.txt", research_results.get("overview", "No overview available."))
        competitors_content = "\n".join(research_results.get("competitors", ["No competitors listed."]))
        competitors_link = upload_text_file(service, company_folder_id, "competitors.txt", competitors_content)

        # 4. Save extracted Markdown articles
        st.info("Saving extracted articles...")
        article_links = []
        for i, article in enumerate(extracted_articles):
            file_name = f"article_{i+1}.md"
            content = f"# {article.get('title', 'Untitled Article')}\n\nSource: {article.get('url', 'N/A')}\n\n{article.get('markdown_content', 'No content extracted.')}"
            link = upload_text_file(service, company_folder_id, file_name, content, mime_type='text/markdown')
            if link:
                article_links.append(link)
        
        # Get the webViewLink for the created company folder
        company_folder_info = service.files().get(fileId=company_folder_id, fields='webViewLink').execute()
        return company_folder_info.get('webViewLink')

    except Exception as e:
        st.error(f"Error saving research to Google Drive: {e}")
        return None