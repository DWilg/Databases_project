import time
import csv
import pandas as pd
import pymysql
import psycopg2
from pymongo import MongoClient
import redis
import matplotlib.pyplot as plt
import logging

# Ustawienia logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Liczba powtórzeń każdego zapytania
REPEATS = 1

# Lista zapytań do wykonania
queries = {
    # easy_1 - łatwe 1
    "rides_by_lyft": {
        "sql": "SELECT * FROM Ride WHERE cab_type = 'Lyft';",
        "mongo": {"cab_type": "Lyft"},
        "redis": '@cab_type:Lyft'
    },
    # easy_2 - łatwe 2
    "rides_from_north_station": {
        "sql": "SELECT * FROM Ride WHERE source = 'North Station';",
        "mongo": {"source": "North Station"},
        "redis": '@source:"North Station"'
    },
    # medium_1 - średniozaawansowane 1
    "price_distance_filter": {
        "sql": "SELECT * FROM Price WHERE distance > 2 AND price < 30 ORDER BY price DESC;",
        "mongo": {"price.distance": {"$gt": 2}, "price.price": {"$lt": 30}},
        "redis": '@price_distance:[2 +inf] @price_price:[-inf 30]'
    },
    # medium_2 - sredniozaawansowane 2
    "rides_in_december": {
        "sql": "SELECT * FROM Time WHERE month = 12;",
        "mongo": {"time.month": 12},
        "redis": '@month:[12 12]'
    },
    # adv_1 - zaawansowane 1
    "ride_names_temp_above_40": {
        "sql": """SELECT r.name FROM Ride r
                 JOIN Weather w ON r.weather_id = w.id
                 JOIN Temperature t ON w.temperature_id = t.id
                 WHERE t.temperatureHigh > 40;""",
        "mongo": {"weather.temperature.temperatureHigh": {"$gt": 40}},
        "redis": '@temp_high:[40 +inf]'
    },
    # adv_2 - zaawansowane 2 
    "rides_wind_gt5_humidity_lt07": {
        "sql": """SELECT r.* FROM Ride r
                 JOIN Weather w ON r.weather_id = w.id
                 JOIN Wind wi ON w.wind_id = wi.id
                 WHERE wi.windSpeed > 5 AND w.humidity < 0.7;""",
        "mongo": {
            "weather.wind.windSpeed": {"$gt": 5},
            "weather.humidity": {"$lt": 0.7}
        },
        "redis": '@wind_speed:[5 +inf] @weather_humidity:[-inf 0.7]'
    },
    # complex_1 - złożone 1
    "avg_price_by_cab_type": {
        "sql": """SELECT r.cab_type, AVG(p.price)
                 FROM Ride r
                 JOIN Price p ON r.price_id = p.id
                 GROUP BY r.cab_type;""",
        "mongo": "agg_avg_price",
        "redis": "agg_avg_price"
    },
    # complex_2 - złożone 2
    "ride_counts_by_hour": {
        "sql": """SELECT t.hour, COUNT(*) FROM Ride r
                 JOIN Time t ON r.time_id = t.id
                 GROUP BY t.hour;""",
        "mongo": "agg_count_hour",
        "redis": "agg_count_hour"
    }
}

# Połączenia

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
    )['example_pg_db']  # collection assumed to be inside

def get_redis_conn():
    return redis.Redis(
        host='localhost',
        port=6379,
        # password='example_redis_password',
        decode_responses=True
    )

# Funkcja benchmarkująca
def benchmark(func):
    start = time.time()
    for _ in range(REPEATS):
        func()
    return round(time.time() - start, 4)

# Zapytania MongoDB agregacyjne
def mongo_aggregate(db, qtype):
    if qtype == "agg_avg_price":
        return list(db.rides.aggregate([
            {"$group": {"_id": "$cab_type", "avgPrice": {"$avg": "$price.price"}}}
        ]))
    elif qtype == "agg_count_hour":
        return list(db.rides.aggregate([
            {"$group": {"_id": "$time.hour", "count": {"$sum": 1}}}
        ]))

# Redis agregacje (wymaga RediSearch)
def redis_aggregate(r, qtype):
    if qtype == "agg_avg_price":
        try:
            return r.execute_command(
                "FT.AGGREGATE", "rides_index", "*",
                "GROUPBY", "1", "@cab_type",
                "REDUCE", "AVG", "1", "@price_price", "AS", "avgPrice"
            )
        except redis.exceptions.ResponseError as e:
            logger.error(f"Redis error: {e}")
            return None
    elif qtype == "agg_count_hour":
        try:
            return r.execute_command(
                "FT.AGGREGATE", "rides_index", "*",
                "GROUPBY", "1", "@time.hour", 
                "REDUCE", "COUNT", "0", "AS", "count"
            )
        except redis.exceptions.ResponseError as e:
            logger.error(f"Redis error: {e}")
            return None

# Benchmarkowanie
results = []

mysql_conn = get_mysql_conn()
pg_conn = get_pg_conn()
mongo_db = get_mongo_conn()
redis_conn = get_redis_conn()

mysql_cursor = mysql_conn.cursor()
pg_cursor = pg_conn.cursor()
mongo_coll = mongo_db["rides"]

for label, q in queries.items():
    logger.info(f"Benchmarking query: {label}")

    # MySQL
    def mysql_q():
        mysql_cursor.execute(q["sql"])
        mysql_cursor.fetchall()
    mysql_time = benchmark(mysql_q)
    logger.info(f"MySQL query {label} time: {mysql_time}s")

    # PostgreSQL
    def pg_q():
        pg_cursor.execute(q["sql"])
        pg_cursor.fetchall()
    pg_time = benchmark(pg_q)
    logger.info(f"PostgreSQL query {label} time: {pg_time}s")

    # MongoDB
    if isinstance(q["mongo"], dict):
        def mongo_q():
            list(mongo_coll.find(q["mongo"]))
    else:
        def mongo_q():
            mongo_aggregate(mongo_db, q["mongo"])
    mongo_time = benchmark(mongo_q)
    logger.info(f"MongoDB query {label} time: {mongo_time}s")

    # Redis
    if "agg" in q["redis"]:
        def redis_q():
            redis_aggregate(redis_conn, q["redis"])
    else:
        def redis_q():
            redis_conn.execute_command("FT.SEARCH", "rides_index", q["redis"])
    redis_time = benchmark(redis_q)
    logger.info(f"Redis query {label} time: {redis_time}s")

    results.append({
        "query": label,
        "mysql_time": mysql_time,
        "postgres_time": pg_time,
        "mongo_time": mongo_time,
        "redis_time": redis_time
    })

# Zapis do CSV
df = pd.DataFrame(results)
df.to_csv("query_benchmark.csv", index=False)
logger.info("Benchmark zakończony — wyniki zapisane do query_benchmark.csv")

# Wykres
df.set_index("query")[["mysql_time", "postgres_time", "mongo_time", "redis_time"]].plot(kind='bar', figsize=(12, 6))
plt.title("Porównanie czasów zapytań (s)")
plt.ylabel("Czas (s)")
plt.xlabel("Typ zapytania")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend(title="Baza danych")
plt.savefig("query_benchmark_chart.png", dpi=300)
plt.show()
