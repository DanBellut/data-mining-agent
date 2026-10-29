import asyncio
import json
import ollama
import pandas as pd
import streamlit as st
from twikit import Client

MODEL = "llama3"
SEARCH_QUERY = "earthquake OR resigned OR bomb OR explosion"

# Category name -> column header in the dashboard
SECTORS = {
    "Natural Disaster": "🌋 Natural Disasters",
    "Resignation": "💼 Resignations",
    "Act of Terror": "🚨 Acts of Terror",
}
CATEGORIES = [*SECTORS, "Irrelevant"]

SYSTEM_PROMPT = f"""
You are an AI data mining assistant. Analyze the social media post sent by the user.
Classify it into EXACTLY ONE of these categories: {json.dumps(CATEGORIES)}.
Provide a very short summary (maximum 10 words) in English.

Respond only with a JSON object in this format:
{{"category": "Category Name", "summary_en": "English summary"}}
""".strip()


async def fetch_real_x_data(username, email, password, search_query, max_tweets=5):
    """
    Fetches live data from X. Credentials are provided by the user
    via the UI and are kept purely in volatile memory (RAM).
    """
    # A new client per request, so sessions of different users are never shared
    client = Client("en-US")
    await client.login(auth_info_1=username, auth_info_2=email or None, password=password)

    results = await client.search_tweet(f"{search_query} lang:en", product="Latest")
    return [
        {
            "source": "X (Twitter)",
            "author": f"@{tweet.user.screen_name}",
            "text": tweet.text,
        }
        for tweet in results[:max_tweets]
    ]


def analyze_post_with_llm(post_text):
    """
    Passes the post text to the local LLM for 3-sector classification.
    """
    try:
        response = ollama.chat(
            model=MODEL,
            # The post is sent as its own message, so it cannot override the instructions
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": post_text},
            ],
            format="json",  # Enforces valid JSON
            options={"temperature": 0},
        )
        data = json.loads(response["message"]["content"])
    except Exception as e:
        return "Irrelevant", f"Analysis failed: {e}"

    # Validate the response instead of trusting it blindly
    category = data.get("category")
    if category not in CATEGORIES:
        category = "Irrelevant"
    return category, str(data.get("summary_en", "No summary available"))


def main():
    st.set_page_config(page_title="Crisis & Politics Data Mining", layout="wide")
    st.title("📊 Global Event Data Miner")
    st.subheader("Data Mining Prototype Powered by Local LLM (Llama 3)")

    # Credential input via the sidebar
    with st.sidebar:
        st.header("🔑 X (Twitter) Credentials")
        st.write("Please use a test account. Credentials are never stored permanently.")
        user_x = st.text_input("X Username")
        email_x = st.text_input("X Email (if required)")
        pass_x = st.text_input("X Password", type="password")

    if st.button("Mine Live Data from X", type="primary"):
        if not user_x or not pass_x:
            st.warning("Please provide your X credentials in the sidebar first.")
            return

        with st.spinner("Connecting to X and collecting data..."):
            try:
                raw_posts = asyncio.run(fetch_real_x_data(user_x, email_x, pass_x, SEARCH_QUERY))
            except Exception as e:
                st.error(f"Scraping error: {e}")
                return

        if not raw_posts:
            st.info("No posts found for the current search.")
            return

        processed_data = []
        progress_bar = st.progress(0, text="AI analyzing posts...")

        for i, post in enumerate(raw_posts):
            category, summary_en = analyze_post_with_llm(post["text"])
            processed_data.append({**post, "category": category, "summary_en": summary_en})
            progress_bar.progress((i + 1) / len(raw_posts), text=f"AI analyzed {i + 1} of {len(raw_posts)} posts")

        st.session_state["mined_data"] = pd.DataFrame(processed_data)
        st.success("Analysis complete!")

    # UI columns layout for the three target sectors
    if "mined_data" in st.session_state:
        df = st.session_state["mined_data"]

        for column, (category, header) in zip(st.columns(len(SECTORS)), SECTORS.items()):
            with column:
                st.header(header)
                sub_df = df[df["category"] == category]
                if sub_df.empty:
                    st.info("No current records.")
                for _, row in sub_df.iterrows():
                    with st.expander(f"📌 {row['summary_en']}"):
                        st.write(f"**Author:** {row['author']}")
                        st.text(row["text"])  # Plain text, so posts cannot inject Markdown

        with st.expander(f"Irrelevant posts ({(df['category'] == 'Irrelevant').sum()})"):
            st.dataframe(df[df["category"] == "Irrelevant"][["author", "text", "summary_en"]])


if __name__ == "__main__":
    main()
README.md
# Data Mining Agent

A Streamlit app that collects recent public posts from X (Twitter) and uses a local LLM to sort them into crisis categories, so breaking events can be spotted without scrolling through noisy feeds.

> **Status:** Early prototype.

## Features

- **X data collection:** Searches recent English posts on X for crisis keywords (earthquake, resigned, bomb, explosion) using Twikit.
- **Local LLM classification:** Uses Llama 3 via Ollama in JSON mode with `temperature=0` to sort each post into Natural Disaster, Resignation, Act of Terror or Irrelevant. No post data leaves your machine.
- **Output validation:** Categories outside the allowed list are treated as irrelevant instead of silently entering the dashboard.
- **Prompt injection protection:** Instructions and post text are sent as separate messages, so a post cannot override the prompt.
- **Short summaries:** Each relevant post gets an English summary of at most 10 words.
- **Streamlit dashboard:** One column per crisis category, plus a collapsible list of posts filtered out as irrelevant.
- **In-memory credentials:** X login data is only kept in memory and never written to disk.

## Usage

```bash
pip install -r requirements.txt
ollama pull llama3
streamlit run data-mining-agent.py
```

Enter the login data of an X test account in the sidebar and click **Mine Live Data from X**.

## Important note

Twikit is an unofficial library that logs in like a browser. Automated access this way may violate X's Terms of Service and can get the account locked. Use a test account only. For production use, the official X API is the proper choice.

## Roadmap

Official X API · additional sources (TikTok, Bluesky, news feeds) · SQLite storage · scheduled monitoring with alerts
