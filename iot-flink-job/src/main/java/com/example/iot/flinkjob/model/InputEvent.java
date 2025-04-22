package com.example.iot.flinkjob.model;

public class InputEvent { // Made class non-public or move to own file
    public String deviceID;
    public String countryID;
    public long timestamp;
    public double value;
    public String potentiallyDirtyField;
    // Default constructor needed for Jackson
    public InputEvent() {}
    // Add getters/setters or ensure fields are public
    // Override toString() for potentially easier debugging if needed
    @Override
    public String toString() {
        return "InputEvent{" +
               "deviceID='" + deviceID + '\'' +
               ", countryID='" + countryID + '\'' +
               ", timestamp=" + timestamp +
               ", value=" + value +
               ", potentiallyDirtyField='" + potentiallyDirtyField + '\'' +
               '}';
    }
}

