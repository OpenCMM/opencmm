# Listener
Get coordinate data from MTConnect agent and distance data from the esp32

1. Start listening coordinate data from MTConnect agent
2. Send ‘startStreaming’ message to the sensor as it detects moving from coordinate data
3. Combine the sensor data with coordinate data and store it in SQLite
4. Send ‘stopStreaming’ message to the sensor as it detects the process end from coordinate data
