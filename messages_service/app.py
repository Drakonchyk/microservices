from flask import Flask, jsonify
messages_service = Flask(__name__)

@messages_service.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "not implemented yet"})

if __name__ == '__main__':
    messages_service.run(host='0.0.0.0', port=5002)