# MyMacros 🥗

A full stack nutrition tracker built with Python, Flask, and SQLite. Search for foods, track your daily macros, and get personalised nutrition advice from an AI assistant.

## Features
- 🔍 Search foods via the Open Food Facts API (3M+ products)
- 📊 View detailed macro breakdown (calories, protein, carbs, fat)
- 📋 Log meals and track daily calorie intake
- 🤖 AI nutrition assistant powered by Groq that reads your actual logged data
- 💾 Persistent storage with SQLite
- 🌙 Clean dark UI with smooth animations

## Technologies Used
- Python 3
- Flask (web framework)
- SQLite (via Python's built-in `sqlite3` module)
- Open Food Facts API
- Groq API (Llama 3.3 70B)
- HTML/CSS (custom dark theme)

## Setup
1. Clone the repository
2. Install dependencies:
3. Create a '.env' file based on '.env.example':
4. Get a free Groq API key at [console.groq.com](https://console.groq.com)
5. Run the app:
6. Visit `http://localhost:5000` in your browser

## What I Learned
- Building a full stack web app with Flask
- Integrating external REST APIs and handling errors gracefully
- Designing and querying a SQLite database
- Securing API keys with environment variables
- Integrating an AI model with real user data as context
- Building a responsive dark UI with CSS animations
