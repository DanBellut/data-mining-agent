import streamlit as st
import pandas as pd
import ollama
import json
import asyncio
from twikit import Client

# Initialize the X (Twitter) client (remains completely neutral)
X_CLIENT = Client('en-US')

async def fetch_real_x_data(username, email, password, search_query, max_tweets=5):
    """
    Fetches live data from X. Credentials are provided by the user 
    via the UI and are kept purely in volatile memory (RAM).
    """
    tweets_data = []
    try:
        # Authentication happens in memory without storing session files
        auth_info = email if email else username
        await X_CLIENT.login(auth_info=auth_info, password=password)
        
        full_query = f"{search_query} lang:en"
        results = await X_CLIENT.search_tweet(full_query, product='Latest')
        
        for tweet in results[:max_tweets]:
            tweets_data.append({
                "source": "X (Twitter)",
                "author": f"@{tweet.user.screen_name}",
                "text": tweet.text
            })
    except Exception as e:
        st.error(f"Scraping error: {e}")
    
    return tweets_data

def analyze_post_with_llm(post_text):
    """
    Passes the tweet text to the local LLM for 3-sector classification.
    """
    prompt = f"""
    You are an AI data mining assistant. Analyze the following social media post text.
    Classify it into EXACTLY ONE of these categories: "Natural Disaster", "Resignation", "Act of Terror", or "Irrelevant".
    Provide a very short summary (maximum 10 words) in English.

    Post text: "{post_text}"

    You MUST respond ONLY with a valid JSON object. Do not include markdown blocks like ```json ... ```. Do not include any introductory text.
    Format your response EXACTLY like this:
    {{"category": "Category Name", "summary_en": "English summary"}}
    """
    try:
        response = ollama.generate(model='llama3', prompt=prompt)
        data = json.loads(response['response'].strip())
        return data.get("category", "Irrelevant"), data.get("summary_en", "No summary available")
    except:
        return "Irrelevant", "Analysis failed"

def main():
    st.set_page_config(page_title="Crisis & Politics Data Mining", layout="wide")
    st.title("📊 Global Event Data Miner")
    st.subheader("Data Mining Prototype Powered by Local LLM (Llama 3)")

    # Secure credential input via the sidebar
    with st.sidebar:
        st.header("🔑 X (Twitter) Credentials")
        st.write("Please enter test account credentials. Data is never stored permanently.")
        user_x = st.text_input("X Username")
        email_x = st.text_input("X Email (if required)")
        pass_x = st.text_input("X Password", type="password")

    keywords = "earthquake OR resigned OR bomb OR explosion"

    if st.button("Mine Live Data from X", type="primary"):
        if not user_x or not pass_x:
            st.warning("Please provide your X credentials in the sidebar first.")
            return

        with st.spinner("Connecting to X and collecting data..."):
            raw_posts = asyncio.run(fetch_real_x_data(user_x, email_x, pass_x, keywords, max_tweets=5))
            
        if not raw_posts:
            st.error("No data received. Please check credentials or X rate limits.")
            return

        processed_data = []
        progress_bar = st.progress(0)
        
        for i, post in enumerate(raw_posts):
            st.write(f"AI analyzing post {i+1} of {len(raw_posts)}...")
            category, summary_en = analyze_post_with_llm(post['text'])
            
            processed_data.append({
                "source": post['source'],
                "author": post['author'],
                "text": post['text'],
                "category": category,
                "summary_en": summary_en
            })
            progress_bar.progress((i + 1) / len(raw_posts))
            
        st.session_state['mined_data'] = pd.DataFrame(processed_data)
        st.success("Analysis complete!")

    # UI columns layout for the three target sectors
    if 'mined_data' in st.session_state:
        df = st.session_state['mined_data']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.header("🌋 Natural Disasters")
            sub_df = df[df['category'] == 'Natural Disaster']
            if sub_df.empty: st.info("No current records.")
            for _, row in sub_df.iterrows():
                with st.expander(f"📌 {row['summary_en']}"):
                    st.write(f"**Author:** {row['author']}")
                    st.italic(f'"{row["text"]}"')

        with col2:
            st.header("💼 Resignations")
            sub_df = df[df['category'] == 'Resignation']
            if sub_df.empty: st.info("No current records.")
            for _, row in sub_df.iterrows():
                with st.expander(f"📌 {row['summary_en']}"):
                    st.write(f"**Author:** {row['author']}")
                    st.italic(f'"{row["text"]}"')

        with col3:
            st.header("🚨 Acts of Terror")
            sub_df = df[df['category'] == 'Act of Terror']
            if sub_df.empty: st.info("No current records.")
            for _, row in sub_df.iterrows():
                with st.expander(f"📌 {row['summary_en']}"):
                    st.write(f"**Author:** {row['author']}")
                    st.italic(f'"{row["text"]}"')

if __name__ == "__main__":
    main()
