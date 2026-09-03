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
2. Install dependencies:
3. Create a `.env` file based on `.env.example`:
4. Get a free Groq API key at [console.groq.com](https://console.groq.com)
5. Run the app:
6. Visit `http://localhost:5000` in your browser

## What I Learned
- Building a full stack web app with Flask
- Integrating external REST APIs with retry logic and error handling
- Designing and querying a SQLite database
- Implementing AI agents with tool calling (search, log, clear)
- Using pre-trained computer vision models for food recognition
- Securing API keys with environment variables
- Building a responsive dark UI with CSS animations

## Problems I ran into
