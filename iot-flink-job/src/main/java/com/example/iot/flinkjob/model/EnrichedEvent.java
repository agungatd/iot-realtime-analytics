package com.example.iot.flinkjob.model;

public class EnrichedEvent {
    public String deviceID;
    public String countryID;
    public double value;
    public String enrichmentData; // Data from external API
    public String transformedValue; // Data from UDF
     // Getters/Setters/Constructors or public fields
}
