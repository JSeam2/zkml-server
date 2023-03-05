from flask import Flask, request, jsonify, send_file
import os
import uuid
import subprocess
import traceback


app = Flask("ZKML-server")
ezkl = "./ezkl/target/release/ezkl"

# flags to only allow for only one proof
# the server cannot accomodate more than one proof
loaded_onnxmodel = None
loaded_inputdata = None
loaded_proofname = None
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

    return send_file(os.path.join("inputdata", sanitized_filename), as_attachment=True)

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

    return send_file(os.path.join("onnxmodel", sanitized_filename), as_attachment=True)

"""
Lists all generated data stored on the server
"""
@app.route('/list/generated', methods=['GET'])
def list_generated():
    filelist = os.listdir(os.path.join('generated'))
    filelist.remove('.gitkeep')
    return jsonify({
        "list": filelist
    })

"""
Download generated data stored on the server
"""
@app.route('/download/generated/<filename>', methods=['GET'])
def download_generated(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("generated", sanitized_filename), as_attachment=True)

"""
Sets the model and input to be used
"""
@app.route('/run/initialize', methods=['GET', 'POST'])
def set_model_input():
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    if request.method == "POST":
        if running:
            return "Already running please wait for completion", 400

        content = request.json
        inputdata = content['inputdata'].strip()
        onnxmodel = content['onnxmodel'].strip()

        loaded_inputdata = os.path.join("inputdata", inputdata)
        loaded_onnxmodel = os.path.join("onnxmodel", onnxmodel)

        loaded_proofname = "inputdata_" + loaded_inputdata[10:46] \
            + "+" + "onnxmodel_" + loaded_onnxmodel[10:46]

        return jsonify({
            "loaded_inputdata": loaded_inputdata,
            "loaded_onnxmodel": loaded_onnxmodel,
            "proof_name": loaded_proofname
        })

    if request.method == "GET":
        return jsonify({
            "loaded_inputdata": loaded_inputdata,
            "loaded_onnxmodel": loaded_onnxmodel,
            "proof_name": loaded_proofname
        })


"""
Generates evm proof
"""
@app.route('/run/gen_evm_proof', methods=['GET'])
def gen_evm_proof():
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    global running
    if loaded_inputdata is None or loaded_onnxmodel is None or loaded_proofname is None:
        return "Input Data or Onnx Model not loaded", 400
    if running:
        return "Already running please wait for completion", 400
    if os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".pf")) or \
        os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".vk")):
        return "Proof already exists", 400

    try:
        running = True
        p = subprocess.run([
                ezkl,
                "--bits=16",
                "-K=17",
                "prove",
                "-D", os.path.join(os.getcwd(), loaded_inputdata),
                "-M", os.path.join(os.getcwd(), loaded_onnxmodel),
                "--proof-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".pf"),
                "--vk-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".vk"),
                "--params-path=" + os.path.join(os.getcwd(), "kzg.params"),
                "--transcript=evm"
            ],
            capture_output=True,
            text=True
        )

        running = False

        return jsonify({
            "stdout": p.stdout,
            "stderr": p.stderr
        })

    except:
        err = traceback.format_exc()
        return "Something bad happened! Please inform the server admin\n" + err, 500

"""
Generates evm verifier
"""
@app.route('/run/gen_evm_verifier', methods=['GET'])
def gen_evm_verifier():
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    global running
    if loaded_inputdata is None or loaded_onnxmodel is None or loaded_proofname is None:
        return "Input Data or Onnx Model not loaded", 400
    if running:
        return "Already running please wait for completion", 400
    if os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol")) or \
        os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".code")):
        return "Verifier already exists", 400

    try:
        running = True
        p = subprocess.run([
                ezkl,
                "--bits=16",
                "-K=17",
                "create-evm-verifier",
                "-D", os.path.join(os.getcwd(), loaded_inputdata),
                "-M", os.path.join(os.getcwd(), loaded_onnxmodel),
                "--deployment-code-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".code"),
                "--vk-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".vk"),
                "--params-path=" + os.path.join(os.getcwd(), "kzg.params"),
                "--sol-code-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol"),
            ],
            capture_output=True,
            text=True
        )

        running = False

        return jsonify({
            "stdout": p.stdout,
            "stderr": p.stderr
        })

    except:
        err = traceback.format_exc()
        return "Something bad happened! Please inform the server admin\n" + err, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)