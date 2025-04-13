import time
import random
import matplotlib.pyplot as plt
import csv

from pymongo import MongoClient
from bson import ObjectId
import psycopg2
import mysql.connector
import redis
import json

NUM_RUNS = 100
delete_results = {}
all_timings = {
    "MongoDB": [],
    "PostgreSQL": [],
    "MySQL": [],
    "Redis": []
}

# === MongoDB ===
def test_mongodb_delete():
    client = MongoClient('mongodb://example_mongo_user:example_mongo_password@localhost:27017/')
    db = client["example_pg_db"]
    collection = db["rides"]

    for _ in range(NUM_RUNS):
        result = collection.insert_one({
            "source": "test", "destination": "test", "price": {"price": 10},
            "cab_type": "test", "product_id": "test", "name": "test",
            "time": {"hour": 1, "day": 1, "month": 1, "datetime": "2022-01-01", "timezone": "UTC"},
            "weather": {}
        })
        record_id = result.inserted_id

        start = time.perf_counter()
        collection.delete_one({"_id": record_id})
        end = time.perf_counter()

        duration = (end - start) * 1000
        all_timings["MongoDB"].append(duration)

    delete_results["MongoDB"] = sum(all_timings["MongoDB"]) / NUM_RUNS

# === PostgreSQL ===
def test_postgresql_delete():
    conn = psycopg2.connect(
        host='localhost', user='example_pg_user', password='example_pg_password',
        dbname='example_pg_db', port=5432
    )
    cursor = conn.cursor()

    for _ in range(NUM_RUNS):
        cursor.execute("""
            INSERT INTO Price (price, distance, surge_multiplier, latitude, longitude)
            VALUES (10, 1.0, 1, 0, 0) RETURNING id;
        """)
        price_id = cursor.fetchone()[0]
        conn.commit()

        start = time.perf_counter()
        cursor.execute("DELETE FROM Price WHERE id = %s;", (price_id,))
        conn.commit()
        end = time.perf_counter()

        duration = (end - start) * 1000
        all_timings["PostgreSQL"].append(duration)

    conn.close()
    delete_results["PostgreSQL"] = sum(all_timings["PostgreSQL"]) / NUM_RUNS

# === MySQL ===
def test_mysql_delete():
    conn = mysql.connector.connect(
        host='localhost', user='example_user', password='example_password',
        database='example_db', port=3306
    )
    cursor = conn.cursor()

    for _ in range(NUM_RUNS):
        cursor.execute("""
            INSERT INTO Price (price, distance, surge_multiplier, latitude, longitude)
            VALUES (10, 1.0, 1, 0, 0);
        """)
        conn.commit()
        price_id = cursor.lastrowid

        start = time.perf_counter()
        cursor.execute("DELETE FROM Price WHERE id = %s;", (price_id,))
        conn.commit()
        end = time.perf_counter()

        duration = (end - start) * 1000
        all_timings["MySQL"].append(duration)

    conn.close()
    delete_results["MySQL"] = sum(all_timings["MySQL"]) / NUM_RUNS

# === Redis ===
def test_redis_delete():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    for i in range(NUM_RUNS):
        key = f"ride:test:{i}"
        r.execute_command("JSON.SET", key, "$", json.dumps({
            "source": "test", "destination": "test", "price": {"price": 10}
        }))

        start = time.perf_counter()
        r.delete(key)
        end = time.perf_counter()

        duration = (end - start) * 1000
        all_timings["Redis"].append(duration)

    delete_results["Redis"] = sum(all_timings["Redis"]) / NUM_RUNS

# === Zapis do CSV ===
def save_to_csv():
    with open("delete_timings.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Run", "MongoDB", "PostgreSQL", "MySQL", "Redis"])
        for i in range(NUM_RUNS):
            row = [
                i + 1,
                all_timings["MongoDB"][i],
                all_timings["PostgreSQL"][i],
                all_timings["MySQL"][i],
                all_timings["Redis"][i],
            ]
            writer.writerow(row)

# === RUN TESTS ===
print("Running delete benchmarks...")
test_mongodb_delete()
test_postgresql_delete()
test_mysql_delete()
test_redis_delete()
print("Saving CSV...")
save_to_csv()
print("Done!")

# === WYKRES ===
labels = list(delete_results.keys())
times = list(delete_results.values())

plt.figure(figsize=(10, 6))
plt.bar(labels, times, color=["#4c72b0", "#dd8452", "#55a868", "#c44e52"])
plt.ylabel("Średni czas usunięcia (ms)")
plt.title(f"Średni czas usunięcia rekordu ({NUM_RUNS} prób)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
for i, v in enumerate(times):
    plt.text(i, v + 0.05, f"{v:.2f} ms", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("porownanie_delete_czasow.png", dpi=300)
plt.show()
