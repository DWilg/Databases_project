import time
import csv
import matplotlib.pyplot as plt
import pymysql
import psycopg2
from pymongo import MongoClient
import redis
import json  # Dodaj ten import na początku pliku
# Funkcje połączeniowe (dostosuj dane dostępowe)
def get_mysql_conn():
    return pymysql.connect(
        host='localhost',
        user='example_user',
        password='example_password',
        database='example_db',
        port=3306
    )

def get_pg_conn():
    return psycopg2.connect(
        host='localhost',
        user='example_pg_user',
        password='example_pg_password',
        dbname='example_pg_db',
        port=5432
    )

def get_mongo_conn():
    return MongoClient(
        'mongodb://example_mongo_user:example_mongo_password@localhost:27017/',
        serverSelectionTimeoutMS=3000
    )['example_pg_db']

def get_redis_conn():
    return redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    )

# Funkcje testujące wydajność
def test_mysql(limit=10000):
    conn = get_mysql_conn()
    cursor = conn.cursor()
    
    # Zapytanie łączące wszystkie tabele
    query = """
    SELECT r.*, p.*, t.*, w.*, temp.*, atemp.*, wind.*, cond.*
    FROM Ride r
    JOIN Price p ON r.price_id = p.id
    JOIN Time t ON r.time_id = t.id
    JOIN Weather w ON r.weather_id = w.id
    JOIN Temperature temp ON w.temperature_id = temp.id
    JOIN ApparentTemperature atemp ON w.apparent_temperature_id = atemp.id
    JOIN Wind wind ON w.wind_id = wind.id
    JOIN Conditions cond ON w.conditions_id = cond.id
    LIMIT %s
    """
    
    start_time = time.time()
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    elapsed_time = time.time() - start_time
    
    cursor.close()
    conn.close()
    
    return elapsed_time

def test_postgresql(limit=10000):
    conn = get_pg_conn()
    cursor = conn.cursor()
    
    query = """
    SELECT r.*, p.*, t.*, w.*, temp.*, atemp.*, wind.*, cond.*
    FROM Ride r
    JOIN Price p ON r.price_id = p.id
    JOIN Time t ON r.time_id = t.id
    JOIN Weather w ON r.weather_id = w.id
    JOIN Temperature temp ON w.temperature_id = temp.id
    JOIN ApparentTemperature atemp ON w.apparent_temperature_id = atemp.id
    JOIN Wind wind ON w.wind_id = wind.id
    JOIN Conditions cond ON w.conditions_id = cond.id
    LIMIT %s
    """
    
    start_time = time.time()
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    elapsed_time = time.time() - start_time
    
    cursor.close()
    conn.close()
    
    return elapsed_time

def test_mongodb(limit=10000):
    db = get_mongo_conn()
    collection = db['rides'] 
    
    start_time = time.time()
    results = list(collection.find().limit(limit))
    elapsed_time = time.time() - start_time
    
    return elapsed_time

def test_redis(limit=10000):
    r = get_redis_conn()
    
    keys = r.keys("ride:*")[:limit]
    
    start_time = time.time()
    
    pipe = r.pipeline()
    
    for key in keys:
        pipe.execute_command('JSON.GET', key)
    
    results = []
    for data in pipe.execute():
        try:
            results.append(json.loads(data))
        except json.JSONDecodeError:
            print("Błąd dekodowania JSON")
    
    elapsed_time = time.time() - start_time
    
    return elapsed_time

def run_tests():
    databases = {
        "MySQL": test_mysql,
        "PostgreSQL": test_postgresql,
        "MongoDB": test_mongodb,
        "Redis": test_redis
    }
    
    results = {}
    for name, test_func in databases.items():
        try:
            time_taken = test_func()
            results[name] = time_taken
            print(f"{name}: {time_taken:.4f} sekund")
        except Exception as e:
            print(f"Błąd podczas testowania {name}: {str(e)}")
            results[name] = None
    
    return results

def plot_results(results, filename="database_comparison.png"):
    plt.figure(figsize=(12, 6))
    names = [name for name, time in results.items() if time is not None]
    times = [time for time in results.values() if time is not None]
    
    colors = ['#007ACC', '#336791', '#4DB33D', '#D82C20'][:len(names)]
    bars = plt.bar(names, times, color=colors)
    plt.ylabel('Czas (sekundy)')
    plt.title('Porównanie czasu pobierania 10 000 rekordów z różnych baz danych')
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.4f}',
                 ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def save_to_csv(results, filename="database_results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Database', 'Time (seconds)'])
        for name, time_taken in results.items():
            writer.writerow([name, time_taken])

def main():
    print("Rozpoczynanie testów wydajności...")
    results = run_tests()
    
    print("\nWyniki:")
    for name, time_taken in results.items():
        if time_taken is not None:
            print(f"{name}: {time_taken:.4f} sekund")
        else:
            print(f"{name}: Test nie powiódł się")
    
    plot_results(results)
    save_to_csv(results)
    print("\nWykres zapisany jako 'database_comparison.png'")
    print("Wyniki zapisane jako 'database_results.csv'")

if __name__ == "__main__":
    main()