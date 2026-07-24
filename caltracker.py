import requests
import sqlite3
import datetime

conn = sqlite3.connect("calories.db", check_same_thread=False)
cursor = conn.cursor()

def setup_database():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            date TEXT
        )
    """)
    conn.commit()

def search_food(food):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={food}&json=true"
    headers = {"User-Agent": "calorie-tracker-app/1.0"}
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            return data["products"][0:5]
        except Exception:
            print(f"Attempt {attempt + 1} failed, retrying...")
    print("Could not connect to the API. Please try again.")
    return []

def display_nutrition(product):
    if "nutriments" not in product:
        print("No nutrition data available for this product.")
        return None
    else:
        nutriments = product["nutriments"]
        calories = nutriments.get('energy-kcal_100g', 0)
        protein = nutriments.get('proteins_100g', 0)
        carbs = nutriments.get('carbohydrates_100g', 0)
        fat = nutriments.get('fat_100g', 0)
        print(f"Calories: {calories} kcal")
        print(f"Protein: {protein}g")
        print(f"Carbs: {carbs}g")
        print(f"Fat: {fat}g")
        return calories, protein, carbs, fat

def log_meal(food_name, calories, protein, carbs, fat):
    date = str(datetime.date.today())
    cursor.execute(
        "INSERT INTO logs (food_name, calories, protein, carbs, fat, date) VALUES (?, ?, ?, ?, ?, ?)",
        (food_name, calories, protein, carbs, fat, date)
    )
    conn.commit()

def view_log():
    today = str(datetime.date.today())
    cursor.execute("SELECT food_name, calories, protein, carbs, fat FROM logs WHERE date = ?", (today,))
    logs = cursor.fetchall()
    total = 0
    for i, log in enumerate(logs):
        print(f"{i + 1}. {log[0]} - {log[1]} kcal | Protein: {log[2]}g | Carbs: {log[3]}g | Fat: {log[4]}g")
        total += log[1]
    
    print(f"\nTotal calories today: {total} kcal")



setup_database()

if __name__ == "__main__":
    while True:
        print("\n1. Search food")
        print("2. Quit")
        print("3. View log")

        choice = input("Choose an option: ")

        if choice == "1":
            food = input("Enter a food: ")
            products = search_food(food)
            if not products:
                continue

            for i, product in enumerate(products):
                name = product.get("product_name", "Unknown product")
                print(f"{i+1}. {name}")

            pick = int(input("Which one? ")) - 1
            product = products[pick]
            nutrition = display_nutrition(product)
            if nutrition:
                calories, protein, carbs, fat = nutrition
                food_name = product.get("product_name", "Unknown")
                log_meal(food_name, calories, protein, carbs, fat)
                print("Meal logged!")
        
        elif choice == "2":
            break
        
        elif choice == "3":
            view_log()
