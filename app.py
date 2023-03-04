from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
import json
import subprocess


app = Flask("ZKML-server")
ezkl = "./ezkl/target/release/ezkl"

"""
Simple single session prover
"""
@app.route('/')
def index():
    return "Extend your smart contracts with Gelkin"

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
Lists all input data stored on the server
"""
@app.route('/list/inputdata', methods=['GET'])
def list_inputdata():
    filelist = os.listdir(os.path.join('inputdata'))
    filelist.remove('.gitkeep')
    return jsonify({
        "list": filelist
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
Lists all onnx data stored on the server
"""
@app.route('/list/onnxmodel', methods=['GET'])
def list_onnxmodel():
    filelist = os.listdir(os.path.join('onnxmodel'))
    filelist.remove('.gitkeep')
    return jsonify({
        "list": filelist
    })


"""
Generate EVM Proof and sends proof.pf and proof.vk to user
"""
@app.route('/gen_evm_proof', methods=['POST'])
def gen_evm_proof():
    if request.method == 'POST':
        p = subprocess.run([ezkl], capture_output=True, text=True)

        return jsonify({
            "stdout": p.stdout,
            "stderr": p.stderr
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)