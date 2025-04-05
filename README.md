<!-- Application to use: -->
1. Dbeaver (mySQL, postgreSQL)
2. Another Redis desktop app
3. MongoCompass

<!-- 1.  How to run databases -->

docker-compose up -d

<!-- 2.  How to populate mySQL and postgreSQL with data: -->


unzip -p postgres_dump.zip | docker exec -i my_postgres psql -U example_pg_user -d example_pg_db

unzip -p mysql_dump.zip | docker exec -i my_database mysql -u root -p"example_root_password" example_db

<!-- 3. How to run populate mongoDB data -->

unzip mongodb_dump.zip -d ./unzipped_dump

docker cp ./unzipped_dump/mongodb_dump my_mongo:/data/db/

<!-- After below commend you should have mongo_db folder listed -->
docker exec my_mongo ls -la /data/db/mongodb_dump/


<!-- Below is one commend -->
docker exec my_mongo mongorestore \
  --host=localhost \
  --port=27017 \
  --username=example_mongo_user \
  --password=example_mongo_password \
  --authenticationDatabase=admin \
  --db=mongo_db \
  /data/db/mongodb_dump/mongo_db/


<!-- 4. How to run populate redis data -->
<!-- Below is one commend -->
unzip -p redis_commands.zip redis_commands.txt | docker exec -i my_redis redis-cli -a example_redis_password --pipe 


docker exec -it my_redis redis-cli -a example_redis_password DBSIZE         

<!-- should print:  693071  -->