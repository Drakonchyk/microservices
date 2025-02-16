FROM python:3.11
WORKDIR /app
COPY ../logging.proto /app/
COPY . /app/
RUN pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I/app --python_out=/app --grpc_python_out=/app /app/logging.proto
EXPOSE 5003
CMD ["python", "app.py"]
