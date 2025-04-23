# Title


## Pinot Kafka Ingestion
```
docker exec pinot-controller bin/pinot-admin.sh AddTable \
    -schemaFile /tmp/pinot_config/schemas/iot_events_schema.json \
    -tableConfigFile /tmp/pinot_config/tables/iot_events_realtime_table.json \
    -exec
```
## To Do

-   [ ] Task 1. use avro and schema registry
-   [ ] Task 2. data validation
-   [ ] Task 3. build pipeline monitoring and alerting system
-   [ ] Task 4. visualize data and business metrics

## References
[flink-usecase-chatgpt](https://chatgpt.com/share/68009dd4-19e8-800c-8870-43e93fccfded)
[pinot-kafka-streaming-ingestion](https://docs.pinot.apache.org/basics/getting-started/pushing-your-streaming-data-to-pinot)
