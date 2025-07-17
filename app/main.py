
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ready')
def ready():
    return jsonify({"status": "ready"})

@app.route('/write')
def write():
    return jsonify({"msg": "Data written to Aerospike and PostgreSQL"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
