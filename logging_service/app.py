from concurrent import futures
import grpc
import logging_pb2
import logging_pb2_grpc
import json
import os

LOG_FILE = "/app/logs.json"

class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self):
        self.storage = self.load_storage()

    def load_storage(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_storage(self):
        with open(LOG_FILE, "w") as file:
            json.dump(self.storage, file)

    def LogMessage(self, request, context):
        if request.id in self.storage:
            return logging_pb2.LogResponse(message="Duplicate ignored")
        
        self.storage[request.id] = request.msg
        self.save_storage()
        print(f"Logged message: {request.msg}")
        return logging_pb2.LogResponse(message="Logged successfully")

    def RetrieveMessages(self, request, context):
        return logging_pb2.MessagesResponse(messages=list(self.storage.values()))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
