# Title


## Steps to run the pipeline
- ```
    git clone https://github.com/agungatd/End-to-end-E-commerce-Data-Lakehouse.git
    cd End-to-end-E-commerce-Data-Lakehouse
    ```
- run all the docker services by run this command on terminal 
`docker compose -f ./infra/docker-compose/docker-compose.yml up -d`
- create flinkjob jar by run:
```cd iot-flink-job && mvn clean package```
- open Flink Web UI on brower with the url:
```http://localhost:8081```
- go to `add job` tab and insert the jar from `./iot-flink-job/target/iot-flink-job-1.0-SNAPSHOT.jar`
- after the flink job installed and run successfully, run the data generator 
`python3 ./data_generator/generator_1.py`
- check whether the transformed data has been put into the kafka topic
```
docker exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic transformed-iot-events
```
- For Pinot-Kafka Ingestion run
```
docker exec pinot-controller bin/pinot-admin.sh AddTable \
    -schemaFile /tmp/pinot_config/schemas/iot_events_schema.json \
    -tableConfigFile /tmp/pinot_config/tables/iot_events_realtime_table.json \
    -exec
```
- run query in pinot UI `http://localhost:9000` :
```
select * from "transformed-iot-events" limit 10;
```
and see the transformed data if all the pipeline has been integrated.
## To Do

-   [ ] Task 1. add flink job unit and integration test
-   [ ] Task 2. create data enrichment and aggregation.
-   [ ] Task 3. use avro and schema registry
-   [ ] Task 4. data validation
-   [ ] Task 5. build pipeline monitoring and alerting system
-   [ ] Task 6. visualize data and business metrics

## References
- [flink-usecase-chatgpt](https://chatgpt.com/share/68009dd4-19e8-800c-8870-43e93fccfded)
- [pinot-kafka-streaming-ingestion](https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot)
