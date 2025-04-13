import time
import random
import matplotlib.pyplot as plt

from pymongo import MongoClient
from bson import ObjectId

import psycopg2

import mysql.connector

import redis

results = {}

def test_mongodb():
    client = MongoClient(
        'mongodb://example_mongo_user:example_mongo_password@localhost:27017/',
        serverSelectionTimeoutMS=3000
    )
    db = client["example_pg_db"]
    collection = db["rides"]
    record_id = ObjectId("67f144c61fd8f48fc214971f")

    start = time.perf_counter()
    for _ in range(1000):
        new_price = round(random.uniform(10, 20), 2)
        collection.update_one(
            {"_id": record_id},
            {"$set": {"price.price": new_price}}
        )
    end = time.perf_counter()
    avg_time = (end - start) * 1000 / 1000
    results["MongoDB"] = avg_time

def test_postgresql():
    conn = psycopg2.connect(
        host='localhost',
        user='example_pg_user',
        password='example_pg_password',
        dbname='example_pg_db',
        port=5432
    )
    cursor = conn.cursor()
    price_id = 1

    start = time.perf_counter()
    for _ in range(1000):
        new_price = round(random.uniform(10, 20), 2)
        cursor.execute("UPDATE Price SET price = %s WHERE id = %s", (new_price, price_id))
        conn.commit()
    end = time.perf_counter()
    conn.close()

    avg_time = (end - start) * 1000 / 1000
    results["PostgreSQL"] = avg_time

def test_mysql():
    conn = mysql.connector.connect(
        host='localhost',
        user='example_user',
        password='example_password',
        database='example_db',
        port=3306
    )
    cursor = conn.cursor()
    price_id = 1

    start = time.perf_counter()
    for _ in range(1000):
        new_price = round(random.uniform(10, 20), 2)
        cursor.execute("UPDATE Price SET price = %s WHERE id = %s", (new_price, price_id))
        conn.commit()
    end = time.perf_counter()
    conn.close()

    avg_time = (end - start) * 1000 / 1000
    results["MySQL"] = avg_time

# === Redis ===
def test_redis():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    key = "ride:67f144c61fd8f48fc214982b"  # zakładamy, że obiekt JSON z danymi już tam istnieje

    start = time.perf_counter()
    for _ in range(1000):
        new_price = round(random.uniform(10, 20), 2)
        r.execute_command("JSON.SET", key, "$.price.price", new_price)
    end = time.perf_counter()

    avg_time = (end - start) * 1000 / 1000
    results["Redis"] = avg_time

# Uruchomienie testów
test_mongodb()
test_postgresql()
test_mysql()
test_redis()

# === Wykres porównawczy ===
labels = list(results.keys())
times = list(results.values())

df = pd.DataFrame(list(results.items()), columns=["Database", "Avg_Update_Time_ms"])
df.to_csv("query_update_benchmark.csv", index=False)
print("Wyniki zapisane do update_benchmark.csv")

plt.figure(figsize=(10, 6))
plt.bar(labels, times, color=["#4c72b0", "#dd8452", "#55a868", "#c44e52"])
plt.ylabel("Średni czas aktualizacji (ms)")
plt.title("Średni czas aktualizacji pojedynczego rekordu (1000 prób)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
for i, v in enumerate(times):
    plt.text(i, v + 0.05, f"{v:.2f} ms", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("porownanie_update_czasow.png", dpi=300)
plt.show()
