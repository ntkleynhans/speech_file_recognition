import os
import tempfile
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['POST'])
def root():
    headers = request.headers
    auth = headers.get("X-API-KEY")
    if auth == os.getenv('X_API_KEY'):
        return jsonify({"message": "Authorized"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401

@app.route('/recognize', methods=['POST'])
def upload_file():
    headers = request.headers
    print(headers)
    auth = headers.get("X-API-KEY")
    if auth != os.getenv('X_API_KEY'):
        return jsonify({"message": "Unauthorized"}), 401

    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"message": "Bad Request - no file part in POST"}), 400
    file = request.files['file']
    if file:
        tf = f'{tempfile.NamedTemporaryFile().name}.wav'
        file.save(tf)
        return jsonify({"message": f"File saved!"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0')
