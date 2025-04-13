import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymysql
import psycopg2
from pymongo import MongoClient
import redis
import json
import time

# Konfiguracja połączeń do baz danych
def get_mysql_conn():
    return pymysql.connect(
        host='localhost',
        user='example_user',
        password='example_password',
        database='example_db',
        port=3306
    )

def get_postgresql_conn():
    return psycopg2.connect(
        host='localhost',
        user='example_pg_user',
        password='example_pg_password',
        dbname='example_pg_db',
        port=5432
    )

def get_mongodb_conn():
    return MongoClient(
        'mongodb://example_mongo_user:example_mongo_password@localhost:27017/',
        serverSelectionTimeoutMS=3000
    )['example_pg_db']

def get_redis_conn():
    return redis.Redis(
        host='localhost',
        port=6379,
        # password='example_redis_password',
        decode_responses=True
    )
    

# Funkcje testujące dla różnych baz danych
def test_mysql(limit):
    conn = get_mysql_conn()
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
    cursor.fetchall()
    cursor.close()
    conn.close()
    return (time.time() - start_time) * 1000  # ms

def test_postgresql(limit):
    conn = get_postgresql_conn()
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
    cursor.fetchall()
    cursor.close()
    conn.close()
    return (time.time() - start_time) * 1000  # ms

def test_mongodb(limit):
    db = get_mongodb_conn()
    collection = db['rides']
    
    start_time = time.time()
    list(collection.find().limit(limit))
    return (time.time() - start_time) * 1000  # ms

def test_redis(limit):
    r = get_redis_conn()
    keys = r.keys("ride:*")[:limit]
    
    start_time = time.time()
    
    # Pipelining dla lepszej wydajności
    pipe = r.pipeline()
    for key in keys:
        pipe.execute_command('JSON.GET', key)  # Użycie JSON.GET zamiast GET
    
    results = []
    for data in pipe.execute():
        if data:
            try:
                results.append(json.loads(data))  # Parsowanie danych JSON
            except json.JSONDecodeError:
                pass
    
    return (time.time() - start_time) * 1000  # ms # ms

# Konfiguracja testów
sample_sizes = [100, 1000, 10000]
databases = {
    'MySQL': test_mysql,
    'PostgreSQL': test_postgresql,
    'MongoDB': test_mongodb,
    'Redis': test_redis
}

# Przeprowadzenie testów
results = {db: [] for db in databases}
for size in sample_sizes:
    for db_name, test_func in databases.items():
        try:
            time_ms = test_func(size)
            results[db_name].append(time_ms)
            print(f"{db_name} ({size} records): {time_ms:.2f} ms")
        except Exception as e:
            print(f"Error in {db_name} with size {size}: {str(e)}")
            results[db_name].append(np.nan)

# Tworzenie wykresu
plt.figure(figsize=(12, 7))
colors = {
    'MySQL': '#007ACC',        # Niebieski
    'PostgreSQL': '#336791',   # Ciemnoniebieski
    'MongoDB': '#4DB33D',      # Zielony
    'Redis': '#D82C20'         # Czerwony
}
line_styles = {
    'MySQL': '-',
    'PostgreSQL': '--',
    'MongoDB': '-.',
    'Redis': ':'
}

for db_name, times in results.items():
    plt.plot(sample_sizes, times, 
             label=db_name, 
             color=colors[db_name],
             linestyle=line_styles[db_name],
             linewidth=2.5,
             marker='o',
             markersize=8)

plt.xscale('log')
plt.yscale('log')  # Dodana skala logarytmiczna dla osi Y
plt.xticks(sample_sizes, labels=[f"{size:,}" for size in sample_sizes], fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('Liczba rekordów', fontsize=14, labelpad=10)
plt.ylabel('Czas wykonania (ms) - skala logarytmiczna', fontsize=14, labelpad=10)
plt.title('Porównanie wydajności baz danych przy pobieraniu danych', fontsize=16, pad=20)
plt.grid(True, which="both", ls="--", alpha=0.5)

# Dodanie wartości na wykresie
for db_name, times in results.items():
    for i, (size, time_ms) in enumerate(zip(sample_sizes, times)):
        if not np.isnan(time_ms):
            plt.text(size, time_ms*1.2, f"{time_ms:.1f}", 
                    ha='center', va='bottom',
                    fontsize=10, color=colors[db_name])

plt.legend(fontsize=12, framealpha=0.9)
plt.tight_layout()

# Zapis wykresu
plt.savefig('database_performance_comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# Zapis wyników do CSV
df = pd.DataFrame(results, index=sample_sizes)
df.index.name = 'Liczba rekordów'
df.to_csv('database_performance_results.csv', float_format='%.2f')
print("Wyniki zapisane do database_performance_results.csv")