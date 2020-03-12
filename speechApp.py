import os
import tempfile
import subprocess
import uuid
import json

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

@app.route('/upload', methods=['POST'])
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
        return jsonify({"message": "File saved!"}), 200

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
        tag = str(uuid.uuid4()).replace('-','')

        try:
            complete = subprocess.run(f'./run_rec.sh {tf} {tag}',shell=True,check=True,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)

            with open(f'/tmp/zulu/{tag}/{tag}.merged.ctm', 'r') as f:
                rec_text = f.read()

            os.system(f'mv {tf} /tmp/zulu/{tag}/')
            msg = {"message": f"{rec_text}", "returncode": e.returncode, "stdout": e.stdout.decode('utf-8')
            "stderr": e.stderr.decode('utf-8'), "cmd": e.cmd}
            with open(f'/tmp/zulu/{tag}/{tag}_run_rec.json', 'w') as f:
                json.dump(msg, f)

            return jsonify({"message": f"{rec_text}"}), 200

        except subprocess.CalledProcessError as e:
            os.system(f'mv {tf} /tmp/zulu/{tag}/')
            msg = {"message": "Failed to recognize", "returncode": e.returncode, "stdout": e.stdout.decode('utf-8')
            "stderr": e.stderr.decode('utf-8'), "cmd": e.cmd}
            with open(f'/tmp/zulu/{tag}/{tag}_run_rec.json', 'w') as f:
                json.dump(msg, f)
            return jsonify(msg), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0')
