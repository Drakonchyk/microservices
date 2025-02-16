from concurrent import futures
import grpc
import logging_pb2
import logging_pb2_grpc

class LoggingService(logging_pb2_grpc.LoggingServiceServicer):
    def __init__(self):
        self.storage = {}

    def LogMessage(self, request, context):
        if request.id in self.storage:
            return logging_pb2.LogResponse(message="Duplicate ignored")
        self.storage[request.id] = request.msg
        print(f"Logged message: {request.msg}")
        return logging_pb2.LogResponse(message="Logged successfully")

    def RetrieveMessages(self, request, context):
        return logging_pb2.MessagesResponse(messages=list(self.storage.values()))

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()
