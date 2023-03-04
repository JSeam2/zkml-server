from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
import json
import subprocess


app = Flask("ZKML-server")

"""
Simple single session prover
"""
@app.route('/')
def index():
    return "Welcome to the ZKML-server"

"""
Upload input data for proving, no validation atm
"""
@app.route('/upload/inputdata', methods=['POST'])
def upload_inputdata():
    if request.method == 'POST':
        inputdata = request.files['inputdata']

        uuidval = uuid.uuid4()

        inputdata.save(os.path.join("inputdata", str(uuidval) + ".json"))

        return jsonify({
            "file": str(uuidval) + ".json"
        })

"""
Upload onnx model for proving, no validation atm
"""
@app.route('/upload/onnxmodel', methods=['POST'])
def upload_onnxmodel():
    if request.method == 'POST':
        # save the single onnx file
        inputdata = request.files['onnxmodel']

        uuidval = uuid.uuid4()

        inputdata.save(os.path.join("onnxmodel", str(uuidval) + ".onnx"))

        return jsonify({
            "file": str(uuidval) + ".onnx"
        })

"""
Generate EVM Proof and sends proof.pf and proof.vk to user
"""
@app.route('/gen_evm_proof', methods=['POST'])
def gen_evm_proof():
    if request.method == 'POST':
        print(os.popen("./ezkl/release/ezkl").read())
        return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)