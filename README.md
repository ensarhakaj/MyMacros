# MyMacros 🥗

A full stack AI-powered nutrition tracker built with Python, Flask, and SQLite. Search for foods, scan photos to identify them, track your daily macros, and get personalised nutrition advice from an AI agent.

## Features
- 🔍 Search foods via the Open Food Facts API (3M+ products)
- 📸 Computer vision food recognition — upload a photo to identify your food automatically
- 📊 View detailed macro breakdown (calories, protein, carbs, fat)
- 📋 Log meals and track daily calorie intake
- 🤖 AI nutrition agent powered by Groq (Llama 3) that can search foods, log meals, and clear your log autonomously using tool calling
- 💾 Persistent storage with SQLite
- 🌙 Clean dark UI with purple accent and smooth animations

## Technologies Used
- Python 3
- Flask (web framework)
- SQLite (via Python's built-in `sqlite3` module)
- Open Food Facts API
- Groq API (Llama 3) with tool calling for agentic AI
- Hugging Face Transformers + PyTorch (food image classification)
- HTML/CSS (custom dark theme)

## Setup
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Create a `.env` file based on `.env.example`: GROQ_API_KEY=your_groq_api_key_here
4. Get a free Groq API key at [console.groq.com](https://console.groq.com)
5. Run the app: python app.py
6. Visit `http://localhost:5000` in your browser

## What I Learned
- Building a full stack web app with Flask
- Integrating external REST APIs with retry logic and error handling
- Designing and querying a SQLite database
- Implementing AI agents with tool calling (search, log, clear)
- Using pre-trained computer vision models for food recognition
- Securing API keys with environment variables

## Problems I ran into
- The Open Food Facts API kept returning empty responses with no error message. I didn't know if it was my code or their server. I added a status code check first which showed it was returning 403 Forbidden, then I realised I needed to send a User-Agent header to identify my app. After fixing that it still failed intermittently, so I implemented a retry loop that tries up to 3 times before giving up gracefully. That taught me never to assume an external API will be reliable
- When I added Flask, my database started throwing threading errors because SQLite connections can only be used in the thread that created them. Flask runs in multiple threads so the connection I created at startup couldn't be used in request handlers. I fixed it with check_same_thread=False and learned that web frameworks handle requests concurrently which is something you don't think about when writing scripts.
- Every time I got a Groq model working, it got deprecated within days. I had to migrate three times during development — llama3-70b, llama3-8b, then the tool-use preview model all got shut down. It taught me to never hardcode a specific model version and to always check the provider's deprecation docs before starting.
