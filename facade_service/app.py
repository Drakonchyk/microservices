from flask import Flask, request, jsonify
import grpc
import uuid
import logging_pb2
import logging_pb2_grpc
import time
import logging
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def send_message_with_retry(msg_id, msg, max_retries=3, retry_delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Attempt {attempt} to send message: {msg_id}")
            with grpc.insecure_channel("logging_service:50051") as channel:
                stub = logging_pb2_grpc.LoggingServiceStub(channel)
                response = stub.LogMessage(logging_pb2.LogRequest(id=msg_id, msg=msg))
                logging.info(f"Message sent successfully on attempt {attempt}")
                return response.message
        except grpc.RpcError as e:
            logging.warning(f"Retry {attempt}/{max_retries} failed: {e.code()} - {e.details()}")
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)  # Exponential backoff
            else:
                logging.error(f"Final retry failed: {e.code()} - {e.details()}")
                return f"gRPC Error: {e.code()} - {e.details()}"


def get_messages_from_logging_service():
    with grpc.insecure_channel('logging_service:50051') as channel:
        stub = logging_pb2_grpc.LoggingServiceStub(channel)
        response = stub.RetrieveMessages(logging_pb2.Empty())
        return response.messages
    
def get_messages_from_message_service():
    try:
        response = requests.get("http://messages_service:5002/status")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get messages from messages_service: {e}")
        return {"message": "Error retrieving message service response"}

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Message required"}), 400

    msg_id = str(uuid.uuid4())
    log_result = send_message_with_retry(msg_id, msg)
    
    return jsonify({"message": log_result, "id": msg_id})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    logs = get_messages_from_logging_service()
    message_service_response = get_messages_from_message_service()
    return jsonify({"logs": list(logs), "messages": message_service_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
