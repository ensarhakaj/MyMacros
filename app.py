from flask import Flask, render_template, request, jsonify
from caltracker import search_food, log_meal, view_log, setup_database, cursor
import sqlite3
import datetime
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)

setup_database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    food = request.form["food"]
    products = search_food(food)
    return render_template("results.html", products=products, query=food)

@app.route("/nutrition", methods=["POST"])
def nutrition():
    food_name = request.form["product_name"]
    calories = float(request.form["calories"])
    protein = float(request.form["protein"])
    carbs = float(request.form["carbs"])
    fat = float(request.form["fat"])
    
    log_meal(food_name, calories, protein, carbs, fat)

    return render_template("nutrition.html", 
        food_name=food_name,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat)

@app.route("/log")
def log():
    today = str(datetime.date.today())
    cursor.execute("SELECT food_name, calories, protein, carbs, fat FROM logs WHERE date = ?", (today,))
    logs = cursor.fetchall()
    total = sum(log[1] for log in logs)
    return render_template("log.html", logs=logs, total=total, today=today)

@app.route("/ai", methods=["POST"])
def ai():
    user_message = request.json["message"]
    
    today = str(datetime.date.today())
    cursor.execute("SELECT food_name, calories, protein, carbs, fat FROM logs WHERE date = ?", (today,))
    logs = cursor.fetchall()
    total_calories = sum(log[1] for log in logs)
    
    meals_text = "\n".join([f"- {log[0]}: {log[1]} kcal, protein: {log[2]}g, carbs: {log[3]}g, fat: {log[4]}g" for log in logs])
    
    system_prompt = f"""You are a helpful nutrition assistant. The user has logged these meals today:
{meals_text if meals_text else "No meals logged yet today."}
Total calories today: {total_calories} kcal
Answer the user's questions about their nutrition based on this data. Be concise and friendly."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)