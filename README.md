Data Mining Agent
A Streamlit app that collects recent public posts from X (Twitter) and uses a local LLM to sort them into crisis categories, so breaking events can be spotted without scrolling through noisy feeds.

Status:Early prototype.

Features
data collection: Searches recent English posts on X for crisis keywords (earthquake, resigned, bomb, explosion) using Twikit.
Local LLM classification: Uses Llama 3 via Ollama in JSON mode with `temperature=0` to sort each post into Natural Disaster, Resignation, Act of Terror or Irrelevant. No post data leaves your machine.
Output validation: Categories outside the allowed list are treated as irrelevant instead of silently entering the dashboard.
Prompt injection protection:Instructions and post text are sent as separate messages, so a post cannot override the prompt.
Short summaries: Each relevant post gets an English summary of at most 10 words.
Streamlit dashboard: One column per crisis category, plus a collapsible list of posts filtered out as irrelevant.
In-memory credentials:X login data is only kept in memory and never written to disk.

Enter the login data of an X test account in the sidebar and click **Mine Live Data from X**.

Important note

Twikit is an unofficial library that logs in like a browser. Automated access this way may violate X's Terms of Service and can get the account locked. Use a test account only. For production use, the official X API is the proper choice.

Roadmap

Official X API · additional sources (TikTok, Bluesky, news feeds) · SQLite storage · scheduled monitoring with alerts
