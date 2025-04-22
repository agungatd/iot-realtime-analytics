package com.example.iot.flinkjob;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import com.fasterxml.jackson.databind.ObjectMapper; // Add Jackson

// --- POJO Definition (Only InputEvent is needed now) ---
import com.example.iot.flinkjob.model.*;

public class StreamingJob {

    private static final String KAFKA_BROKERS = "kafka:29092"; // Internal Docker network address
    private static final String INPUT_TOPIC = "iot-events";
    private static final String OUTPUT_TOPIC = "transformed-iot-events"; // Sink to the same or a different topic
    private static final String CONSUMER_GROUP = "iot-event-transformed-group"; // Use a descriptive group id

    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // --- 1. Kafka Source ---
        KafkaSource<String> source = KafkaSource.<String>builder()
            .setBootstrapServers(KAFKA_BROKERS)
            .setTopics(INPUT_TOPIC)
            .setGroupId(CONSUMER_GROUP)
            .setStartingOffsets(OffsetsInitializer.latest())
            .setValueOnlyDeserializer(new SimpleStringSchema())
            .build();

        DataStream<String> kafkaStream = env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka Source");

        // --- 2a. Parse JSON & Basic Cleaning ---
        DataStream<InputEvent> cleanedStream = kafkaStream
            .map(new JsonToInputEventMapper()) // Parse
            .filter(event -> event != null)    // Filter out parsing errors
            .map(new CleanDataMapper());       // Apply cleaning logic

        // --- 2b. Filtering ---
        DataStream<InputEvent> filteredStream = cleanedStream
            .filter(event -> event.value > 0); // Example: filter out zero/negative values
        
        // --- 3. Serialize Cleaned Event back to JSON String ---
        DataStream<String> outputJsonStream = filteredStream
            .map(new InputEventToJsonMapper()); // Convert cleaned object back to JSON

        // --- 4. Kafka Sink ---
         KafkaSink<String> sink = KafkaSink.<String>builder()
            .setBootstrapServers(KAFKA_BROKERS)
            .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                .setTopic(OUTPUT_TOPIC) // Define the output topic
                .setValueSerializationSchema(new SimpleStringSchema()) // Input is already String
                .build()
            )
            // Add delivery guarantees if needed, e.g., .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
            .build();

        // --- 5. Send the resulting JSON strings to Kafka ---
        outputJsonStream.sinkTo(sink).name("Kafka Sink");


        // Execute job
        env.execute("Flink Kafka Basic Cleaning Job"); // Updated Job Name
    }

    // --- Helper Mappers ---

    // 2a. Parse JSON to InputEvent POJO
    public static class JsonToInputEventMapper implements MapFunction<String, InputEvent> {
         private static final ObjectMapper objectMapper = new ObjectMapper(); // Reuse ObjectMapper
         @Override
         public InputEvent map(String value) { // Removed 'throws Exception' for simplicity, handling internally
             try {
                 // Basic check for empty/null strings if necessary
                 if (value == null || value.trim().isEmpty()) {
                     System.err.println("Received null or empty message, skipping.");
                     return null;
                 }
                 return objectMapper.readValue(value, InputEvent.class);
             } catch (Exception e) {
                 // Log error or return null if parsing fails
                 System.err.println("Failed to parse JSON: " + value + " | Error: " + e.getMessage());
                 return null; // Indicate failure to the filter step
             }
         }
    }

    // 2b. Basic Cleaning Logic on InputEvent POJO
    public static class CleanDataMapper implements MapFunction<InputEvent, InputEvent> {
        @Override
        public InputEvent map(InputEvent event) throws Exception {
            if (event.potentiallyDirtyField != null) {
                event.potentiallyDirtyField = event.potentiallyDirtyField.trim().toLowerCase();
            } else {
                // Optional: Handle null field, e.g., set a default or leave as null
                 event.potentiallyDirtyField = "default_value_if_null"; // Example: set default
            }
            // Add other cleaning logic as needed (e.g., default values for other null fields)
            if (event.countryID == null) {
                event.countryID = "ID"; // Example: default country ID
            }
            return event;
        }
    }

    // 3a. Serialize InputEvent POJO back to JSON String
    public static class InputEventToJsonMapper implements MapFunction<InputEvent, String> {
        private static final ObjectMapper objectMapper = new ObjectMapper(); // Reuse ObjectMapper
        @Override
        public String map(InputEvent value) { // Removed 'throws Exception'
            try {
                 return objectMapper.writeValueAsString(value);
            } catch (Exception e) {
                 System.err.println("Failed to serialize InputEvent to JSON: " + value.toString() + " | Error: " + e.getMessage());
                 // Return a specific error JSON or null, depending on how you want to handle sink errors
                 return "{\"error\":\"serialization failed\", \"eventId\":\"" + (value != null ? value.deviceID : "unknown") + "\"}";
            }
        }
    }
}