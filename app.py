from flask import Flask, render_template, request, jsonify
from caltracker import search_food, log_meal, view_log, setup_database, cursor, clear_today_log
import sqlite3
import datetime
import json
from dotenv import load_dotenv
import os
from groq import Groq
import re
import base64
from PIL import Image
import io
import requests as http_requests

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

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_food",
                "description": "Search for a food item and get its nutritional information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The food to search for e.g. chicken breast, banana"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "log_meal",
                "description": "Log a meal to the database with exact nutrition values",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "food_name": {"type": "string", "description": "Name of the food"},
                        "calories": {"type": "number", "description": "Calories in kcal"},
                        "protein": {"type": "number", "description": "Protein in grams"},
                        "carbs": {"type": "number", "description": "Carbohydrates in grams"},
                        "fat": {"type": "number", "description": "Fat in grams"}
                    },
                    "required": ["food_name", "calories", "protein", "carbs", "fat"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_today_log",
                "description": "Get all meals logged today and total calories",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "clear_today_log",
                "description": "Clear all meals logged today",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    system_prompt = f"""You are MyMacros AI — a friendly nutrition assistant. You have access to these tools:
1. search_food(query) — searches for a food and returns its nutrition data
2. log_meal(food_name, calories, protein, carbs, fat) — logs a meal with exact nutrition values
3. get_today_log() — shows today's logged meals
4. clear_today_log() — clears all meals logged today

IMPORTANT RULES:
- When asked to log a food, ALWAYS call search_food first to get the nutrition data
- Only call log_meal AFTER you have the actual calories, protein, carbs and fat values from search_food
- Never guess or estimate nutrition values
- After logging a meal, ALWAYS respond with a friendly confirmation message like "Done! I've logged [food] for you — [calories] kcal, [protein]g protein, [carbs]g carbs, [fat]g fat."
- After clearing the log, confirm it's been cleared
- NEVER just output raw numbers as your response

Today's logged meals:
{meals_text if meals_text else "No meals logged yet."}
Total calories today: {total_calories} kcal"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message)
        
        max_iterations = 5
        iteration = 0
        
        while response_message.tool_calls and iteration < max_iterations:
            iteration += 1
            
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                if tool_name == "search_food":
                    results = search_food(tool_args["query"])
                    if results:
                        product = results[0]
                        nutriments = product.get("nutriments", {})
                        tool_result = {
                            "name": product.get("product_name", "Unknown"),
                            "calories": nutriments.get("energy-kcal_100g", 0),
                            "protein": nutriments.get("proteins_100g", 0),
                            "carbs": nutriments.get("carbohydrates_100g", 0),
                            "fat": nutriments.get("fat_100g", 0)
                        }
                    else:
                        tool_result = {"error": "No results found"}
                        
                elif tool_name == "log_meal":
                    log_meal(
                        tool_args["food_name"],
                        tool_args["calories"],
                        tool_args["protein"],
                        tool_args["carbs"],
                        tool_args["fat"]
                    )
                    tool_result = {"success": f"{tool_args['food_name']} logged successfully"}
                    
                elif tool_name == "get_today_log":
                    cursor.execute("SELECT food_name, calories, protein, carbs, fat FROM logs WHERE date = ?", (today,))
                    today_logs = cursor.fetchall()
                    tool_result = {
                        "meals": [{"name": l[0], "calories": l[1], "protein": l[2], "carbs": l[3], "fat": l[4]} for l in today_logs],
                        "total_calories": sum(l[1] for l in today_logs)
                    }

                elif tool_name == "clear_today_log":
                    clear_today_log()
                    tool_result = {"success": "Today's log has been cleared"}

                else:
                    tool_result = {"error": "Unknown tool"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            next_response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = next_response.choices[0].message
            messages.append(response_message)

        reply = response_message.content or "Done!"
        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
    else:
        reply = response_message.content
        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()

    return jsonify({"reply": reply})

@app.route("/scan", methods=["POST"])
def scan():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"})
    
    file = request.files["image"]
    image_bytes = file.read()
    
    try:
        from transformers import pipeline
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        classifier = pipeline("image-classification", model="nateraw/food")
        results = classifier(image)
        
        if results:
            top_food = results[0]["label"]
            score = results[0]["score"]
            return jsonify({
                "food": top_food,
                "confidence": round(score * 100, 1),
                "all_results": results[:3]
            })
        else:
            return jsonify({"error": "Could not identify food"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)