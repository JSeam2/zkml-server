from flask import Flask, request, jsonify, send_file
import os
import uuid
import subprocess


app = Flask("ZKML-server")
ezkl = "./ezkl/target/release/ezkl"

# flags to only allow for only one proof
# the server cannot accomodate more than one proof
loaded_onnxmodel = None
loaded_inputdata = None
running = False

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
Download input data stored on the server
"""
@app.route('/download/inputdata/<filename>', methods=['GET'])
def download_inputdata(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("inputdata", sanitized_filename))

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
Download input data stored on the server
"""
@app.route('/download/onnxmodel/<filename>', methods=['GET'])
def download_onnxmodel(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("onnxmodel", sanitized_filename))

"""
Sets the model and input to be used
"""
@app.route('/run/initialize', methods=['GET', 'POST'])
def set_model_input():
    global loaded_inputdata
    global loaded_onnxmodel
    if request.method == "POST":

        content = request.json
        inputdata = content['inputdata'].strip()
        onnxmodel = content['onnxmodel'].strip()

        loaded_inputdata = os.path.join("inputdata", inputdata)
        loaded_onnxmodel = os.path.join("onnxmodel", onnxmodel)

        return jsonify({
            "loaded_inputdata": loaded_inputdata,
            "loaded_onnxmodel": loaded_onnxmodel
        })

    if request.method == "GET":
        return jsonify({
            "loaded_inputdata": loaded_inputdata,
            "loaded_onnxmodel": loaded_onnxmodel
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