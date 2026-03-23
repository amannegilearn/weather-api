from fastapi import FastAPI
import requests
from datetime import datetime
import sqlite3
import pandas as pd 
import time
import threading

app = FastAPI()
connection = sqlite3.connect("weather.db",check_same_thread=False)
API_KEY = "189e4a7b830306ca87efc15487b61d55"

@app.get('/')
def home():
    return "welcome to Weather api"



def create_table(connection):
    query = """
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            city TEXT ,
            temperature FLOAT,
            humidity int,
            sunrise TEXT,
            description TEXT,
            created_at DATETIME
            )
"""
    try:
        with connection:
            connection.execute(query)
        print("table is created")
    except Exception as e:
        print(e)
create_table(connection)

@app.get('/weather')
def get_weather(city:str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"]!=200:
                return None

    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    sunrise = data['sys']['sunrise']
    sunrise_time = datetime.fromtimestamp(sunrise).strftime('%H:%M:%S')
    description = data['weather'][0]['description']

    now = datetime.now()

    with connection:
        connection.execute(
            "INSERT INTO users(city, temperature, humidity, sunrise, description, created_at) VALUES (?,?,?,?,?,?)",
            (city, temperature, humidity, sunrise, description, now)
        )
    

    return {
        "city": city,
        "temperature": temperature,
        "humidity": humidity,
        "Sunrise" : sunrise_time,
        "Description" : description
    }

@app.get('/weather/history')
def get_history():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()  
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

@app.get('/weather/history/{city}')
def fetch_data(city:str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE city = ?",(city,))
    rows = cursor.fetchall()
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

@app.get('/weather/stats/{city}')
def show_stats(city:str):
    cursor  = connection.cursor()
    cursor.execute("SELECT temperature, humidity FROM users WHERE city = ?",(city,))
    rows = cursor.fetchall()

    if not rows:
        return f"no data from {city}"
    
    df = pd.DataFrame(rows, columns=["temperature","humidity"])
    avg_temp = df["temperature"].mean()
    min_temp = df["temperature"].min() 
    max_temp = df["temperature"].max()
    avg_hum = df["humidity"].mean()

    return {
        "city" : city,
        "Average temperature" : avg_temp,
        "minimum temperature" : min_temp,
        "maximum temperature" : max_temp,
        "average humidity" : avg_hum
        }

def fetch_store_city(city:str):
    while True:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            if data["cod"]!=200:
                return None

            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            sunrise = data['sys']['sunrise']
            sunrise_time = datetime.fromtimestamp(sunrise).strftime('%H:%M:%S')
            description = data['weather'][0]['description']

            now = datetime.now()

            with connection:
                connection.execute(
                    "INSERT INTO users(city, temperature, humidity, sunrise, description, created_at) VALUES (?,?,?,?,?,?)",
                    (city, temperature, humidity, sunrise, description, now)
                )
            
            
            print(f"data stored for {city} at time {now} ")
        except Exception as e:
            print(e)

        time.sleep(3600)

@app.on_event("startup")
def start_background():
    thread = threading.Thread(target=fetch_store_city,args=("Delhi",))
    thread.daemon = True
    thread.start()