import os
import tempfile
import subprocess
import uuid
import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/speech", methods=['GET'])
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/speech', methods=['POST'])
def root():
    headers = request.headers
    auth = headers.get("X-API-KEY")
    if auth == os.getenv('X_API_KEY'):
        return jsonify({"message": "Authorized"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401

@app.route('/speech/upload', methods=['POST'])
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

@app.route('/speech/recognize', methods=['POST'])
def recognize():
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
            msg = {"message": f"{rec_text}", "returncode": complete.returncode, "stdout": complete.stdout.decode('utf-8'),
            "stderr": complete.stderr.decode('utf-8')}

            os.system(f'python /home/ubuntu/local/scripts/ctm_to_json.py --input_file=/tmp/zulu/{tag}/{tag}.merged.ctm --output_file=/tmp/zulu/{tag}/{tag}.merged.json')
            with open(f'/tmp/zulu/{tag}/{tag}.merged.json', 'r') as f:
                final_msg = json.load(f)
            return jsonify({"message": f"{final_msg}"}), 200

        except subprocess.CalledProcessError as e:
            os.system(f'mv {tf} /tmp/zulu/{tag}/')
            msg = {"message": "Failed to recognize", "returncode": e.returncode, "stdout": e.stdout.decode('utf-8'),
            "stderr": e.stderr.decode('utf-8')}
            with open(f'/tmp/zulu/{tag}/{tag}_run_rec.json', 'w') as f:
                json.dump(msg, f)
            return jsonify(msg), 422

if __name__ == "__main__":
    app.run(host='0.0.0.0')
