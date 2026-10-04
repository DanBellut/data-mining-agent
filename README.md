An automated Python project that collects real-time public data from social networks and filters them into high-relevance crisis categories using a local LLM. 

Instead of manually scrolling through noisy feeds, this tool automatically scans public discourse on X (Twitter) and TikTok, focuses on critical breaking events, and displays them inside a clean, live dashboard.

Features
Data Mining Hub: Simulates and processes live public streams from high-volume platforms (X/Twitter and TikTok) based on custom keyword routing.

AI Classification: Uses a local LLM (Ollama/Llama 3) to filter out social media spam, ensuring posts are strictly categorized into three distinct crisis sectors: Natural Disasters, Political Resignations, and Acts of Terror.

Automated Synthesis: Generates rapid, low-latency summaries in English to provide an immediate overview of global incidents as they happen.

Privacy-First Blueprint: Operates completely in-memory with zero persistent cookie tracking or stored session files, keeping credential handling safe for local deployment.

Built for Scaling: Cleanly decoupled frontend and backend architecture, designed to easily integrate persistent databases (SQLite) and enterprise-grade scraping layers in the future.

Tech Stack
Language: Python 3.10+
Interface: Streamlit
Social Mining: Twikit / Asyncio
AI Processing: Ollama (Llama 3)
