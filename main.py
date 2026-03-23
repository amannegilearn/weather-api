from fastapi import FastAPI
import requests
from datetime import datetime
import sqlite3
import pandas as pd
import time
import threading
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")

DB_NAME = "weather.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_table():
    conn = get_connection()
    query = """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            city TEXT,
            temperature FLOAT,
            humidity INT,
            sunrise TEXT,
            description TEXT,
            created_at DATETIME
        )
    """
    with conn:
        conn.execute(query)
    conn.close()


create_table()


@app.get("/")
def home():
    return {"message": "Weather API is live 🚀"}


def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return None

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
        "description": data["weather"][0]["description"]
    }


@app.get("/weather")
def get_weather(city: str):
    result = fetch_weather(city)

    if not result:
        return {"error": "City not found"}

    conn = get_connection()
    now = datetime.now()

    with conn:
        conn.execute(
            "INSERT INTO users(city, temperature, humidity, sunrise, description, created_at) VALUES (?,?,?,?,?,?)",
            (
                city,
                result["temperature"],
                result["humidity"],
                result["sunrise"],
                result["description"],
                now,
            ),
        )
    conn.close()

    return {
        "city": city,
        **result
    }


@app.get("/weather/history")
def get_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "city": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "sunrise": row[4],
            "description": row[5],
            "created_at": row[6]
        })

    return result


@app.get("/weather/history/{city}")
def fetch_data(city: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE city = ?", (city,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "city": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "sunrise": row[4],
            "description": row[5],
            "created_at": row[6]
        })

    return result


@app.get("/weather/stats/{city}")
def show_stats(city: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, humidity FROM users WHERE city = ?", (city,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"error": f"No data for {city}"}

    df = pd.DataFrame(rows, columns=["temperature", "humidity"])

    return {
        "city": city,
        "avg_temp": df["temperature"].mean(),
        "min_temp": df["temperature"].min(),
        "max_temp": df["temperature"].max(),
        "avg_humidity": df["humidity"].mean()
    }


def fetch_store_city(city: str):
    while True:
        try:
            result = fetch_weather(city)

            if not result:
                print("API error")
                time.sleep(60)
                continue

            conn = get_connection()
            now = datetime.now()

            with conn:
                conn.execute(
                    "INSERT INTO users(city, temperature, humidity, sunrise, description, created_at) VALUES (?,?,?,?,?,?)",
                    (
                        city,
                        result["temperature"],
                        result["humidity"],
                        result["sunrise"],
                        result["description"],
                        now,
                    ),
                )
            conn.close()

            print(f"Stored data for {city}")

        except Exception as e:
            print(e)

        time.sleep(300) 


@app.on_event("startup")
def start_background():
    thread = threading.Thread(target=fetch_store_city, args=("Delhi",))
    thread.daemon = True
    thread.start()