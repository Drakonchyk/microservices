# Flask Microservices System

This project is a microservices-based system built using Flask and gRPC. It consists of three services:

1. Facade Service (API Gateway - port 5003)
2. Logging Service (Stores logs via gRPC - port 50051)
3. Messages Service (Returns static messages - port 5002)

The services communicate using gRPC (for logging) and HTTP (for messages service).

## Features

### Facade Service (API Gateway - 5003)
- Accepts messages via HTTP POST /send_message
- Sends logs to logging_service using gRPC with retry mechanism
- Fetches logs via gRPC and messages from messages_service
- Exposes GET /get_messages for retrieving combined responses

### Logging Service (50051)
- Listens for log messages via gRPC
- Implements exactly-once delivery (deduplication)
- Stores logs persistently in a JSON file
- Provides RetrieveMessages() gRPC method for fetching logs

### Messages Service (5002)
- Returns a static response via GET /status
- Used for testing system integration

## Getting Started

### Clone the Repository
```bash
git clone https://github.com/Drakonchyk/microservices.git
cd microservices
```

### Build and Start All Services
```bash
docker-compose up --build
```

### Verify Services are Running
```bash
docker ps
```
Expected Output:
```
CONTAINER ID   IMAGE                            PORTS                    NAMES
xxxxx          microservices-facade_service     0.0.0.0:5003->5003/tcp   microservices-facade_service-1
xxxxx          microservices-logging_service    0.0.0.0:50051->50051/tcp microservices-logging_service-1
xxxxx          microservices-messages_service   0.0.0.0:5002->5002/tcp   microservices-messages_service-1
```

## API Usage

### Send a Message (facade_service)
```bash
curl -X POST http://localhost:5003/send_message -H "Content-Type: application/json" -d '{"msg": "Hello gRPC"}'
```
Expected Response:
```json
{"id": "some-uuid", "message": "Logged successfully"}
```

### Retrieve Stored Messages (facade_service)
```bash
curl -X GET http://localhost:5003/get_messages
```
Expected Response:
```json
{
  "logs": ["Hello gRPC"],
  "messages": {"message": "not implemented yet"}
}
```

### Test Messages Service Directly
```bash
curl -X GET http://localhost:5002/status
```
Expected Response:
```json
{"message": "not implemented yet"}
```

## Retry & Deduplication Testing

### Stop Logging Service to Simulate Failure
```bash
docker stop microservices-logging_service-1
```

### Send a Message While logging_service is Down
```bash
curl -X POST http://localhost:5003/send_message -H "Content-Type: application/json" -d '{"msg": "Retry Test"}'
```
Expected Response:
```json
{"id":"some-uuid","message":"gRPC Error: ..."}
```

### Restart Logging Service
```bash
docker start microservices-logging_service-1
```

### Send Another Message (Should Work Now)
```bash
curl -X POST http://localhost:5003/send_message -H "Content-Type: application/json" -d '{"msg": "Final Test"}'
```
Expected Response:
```json
{"id":"some-uuid","message":"Logged successfully"}
```

### Retrieve Messages (Ensuring Deduplication Works)
```bash
curl -X GET http://localhost:5003/get_messages
```
Expected Output:
```json
{"logs":["First Message","Second Message","Final Test"],"messages":{"message":"not implemented yet"}}
```

## Summary

### Communication Flow
1. facade_service receives an HTTP POST /send_message request.
2. It sends the message via gRPC to logging_service (with retries).
3. logging_service stores messages with deduplication and after restarting it stores previous data.
4. facade_service fetches logs from logging_service (gRPC) and messages from messages_service (HTTP).
5. GET /get_messages returns both responses combined.

### Technologies Used
- Flask (API Gateway & Messages Service)
- gRPC (Logging Service Communication)
- Docker & Docker Compose
- Python Requests (Message Retrieval)
- Retry Mechanism & Deduplication

