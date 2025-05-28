import os
import google.generativeai as genai
import streamlit as st

def research_company(company_name):
    """
    Researches a company using the Gemini API and returns structured information
    including overview, competitors, and relevant articles with source URLs.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')

        st.info(f"Asking Gemini about {company_name} overview...")
        overview_prompt = f"Provide a concise overview of {company_name}, including its primary business, industry, and key products/services. Keep it to 3-4 sentences."
        overview_response = model.generate_content(overview_prompt)
        overview = overview_response.text if overview_response else "N/A"

        st.info(f"Asking Gemini about {company_name} competitors...")
        competitors_prompt = f"List the top 3-5 direct competitors of {company_name}. Provide only their names, separated by commas."
        competitors_response = model.generate_content(competitors_prompt)
        competitors = [c.strip() for c in competitors_response.text.split(',') if c.strip()] if competitors_response else []

        st.info(f"Asking Gemini for relevant articles about {company_name} and its industry...")
        articles_prompt = f"Find 3-5 recent and relevant news articles or reports about {company_name} or its industry. For each, provide the title and the full URL. Format as: 'Title: [Title]\nURL: [URL]'. Ensure URLs are complete and functional."
        articles_response = model.generate_content(articles_prompt)
        articles_text = articles_response.text if articles_response else ""

        articles = []
        # Simple parsing for "Title: ...\nURL: ..." format
        lines = articles_text.split('\n')
        current_article = {}
        for line in lines:
            if line.startswith("Title:"):
                if current_article: # Save previous article if exists
                    articles.append(current_article)
                current_article = {"title": line.replace("Title:", "").strip(), "url": ""}
            elif line.startswith("URL:"):
                if current_article:
                    current_article["url"] = line.replace("URL:", "").strip()
        if current_article: # Add the last article
            articles.append(current_article)

        return {
            "overview": overview,
            "competitors": competitors,
            "articles": articles
        }

    except Exception as e:
        st.error(f"Error interacting with Gemini API: {e}")
        return {
            "overview": "Error: Could not retrieve overview.",
            "competitors": [],
            "articles": []
        }