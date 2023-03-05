from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import os
import uuid
import subprocess
import traceback
import rpc_endpoint
import solcx
from web3 import Web3


app = Flask("ZKML-server")
cors = CORS(app)

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
@cross_origin()
def index():
    return "Extend your smart contracts with Gelkin"

"""
Upload input data for proving, no validation atm
"""
@app.route('/upload/inputdata', methods=['POST'])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
def download_inputdata(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("inputdata", sanitized_filename), as_attachment=True)

"""
Upload onnx model for proving, no validation atm
"""
@app.route('/upload/onnxmodel', methods=['POST'])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
def download_onnxmodel(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("onnxmodel", sanitized_filename), as_attachment=True)

"""
Lists all generated data stored on the server
"""
@app.route('/list/generated', methods=['GET'])
@cross_origin()
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
@cross_origin()
def download_generated(filename):
    sanitized_filename = str(filename)

    return send_file(os.path.join("generated", sanitized_filename), as_attachment=True)

"""
Sets the model and input to be used
"""
@app.route('/run/initialize', methods=['GET', 'POST'])
@cross_origin()
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
@cross_origin()
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
        running = False
        err = traceback.format_exc()
        return "Something bad happened! Please inform the server admin\n" + err, 500

"""
Generates evm verifier
"""
@app.route('/run/gen_evm_verifier', methods=['GET'])
@cross_origin()
def gen_evm_verifier():
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    global running
    if loaded_inputdata is None or loaded_onnxmodel is None or loaded_proofname is None:
        return "Input Data or Onnx Model not loaded", 400
    if running:
        return "Already running please wait for completion", 400
    if os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol")) and \
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
                "--params-path=" + os.path.join(os.getcwd(), "kzg.params"),
                "--vk-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".vk"),
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
        running = False
        err = traceback.format_exc()
        return "Something bad happened! Please inform the server admin\n" + err, 500

"""
Verifies proof using .code
"""
@app.route('/run/verify', methods=['GET'])
@cross_origin()
def run_verify():
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    global running
    if loaded_inputdata is None or loaded_onnxmodel is None or loaded_proofname is None:
        return "Input Data or Onnx Model not loaded", 400
    if running:
        return "Already running please wait for completion", 400
    if not os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".code")):
        return "Proof does not exists", 400

    try:
        running = True
        p = subprocess.run([
                ezkl,
                "--bits=16",
                "-K=17",
                "verify-evm",
                "--proof-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".pf"),
                "--deployment-code-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".code"),
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
        running = False
        err = traceback.format_exc()
        return "Something bad happened! Please inform the server admin\n" + err, 500

"""
Deploys verifier
"""
@app.route('/run/deploy_verifier/<network_id>', methods=['GET'])
@cross_origin()
def run_deploy(network_id):
    global loaded_inputdata
    global loaded_onnxmodel
    global loaded_proofname
    global running
    network_id = int(network_id)
    if loaded_inputdata is None or loaded_onnxmodel is None or loaded_proofname is None:
        return "Input Data or Onnx Model not loaded", 400
    if running:
        return "Already running please wait for completion", 400
    if not os.path.exists(os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol")):
        return "Proof does not exists", 400

    rpc = rpc_endpoint.ETH_MAINNET
    if network_id == 5:
        rpc = rpc_endpoint.ETH_GOERLI

    if network_id == 5001:
        rpc = rpc_endpoint.MANTLE_TESTNET

    if network_id == 80001:
        rpc = rpc_endpoint.POLYGON_MUMBAI

    try:
        running = True

        # compile contract
        with open(os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol"), "r") as f:
            file = f.read()

        temp_file = solcx.compile_source(file, output_values=["abi", "bin-runtime"])
        abi = temp_file['<stdin>:Verifier']['abi']
        bytecode = temp_file['<stdin>:Verifier']['bin-runtime']
        web3 = Web3(Web3.HTTPProvider(rpc))

        account_from = {
            'private_key': rpc_endpoint.PRIVATE_KEY,
            'address': rpc_endpoint.PUBLIC_KEY,
        }

        contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = web3.eth.get_transaction_count(account_from['address'])

        construct_txn = contract.constructor().buildTransaction(
            {
                'from': account_from['address'],
                'nonce': nonce
            }
        )

        tx_create = web3.eth.account.sign_transaction(construct_txn, account_from['private_key'])

        tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "contractaddr": tx_receipt.contractAddress
        })


        # p = subprocess.run([
        #         ezkl,
        #         "deploy-verifier-evm",
        #         "-S", os.path.join(os.getcwd(), "mnemonic.txt"),
        #         "-U", rpc,
        #         "--sol-code-path", os.path.join(os.getcwd(), "generated", loaded_proofname + ".sol"),
        #     ],
        #     capture_output=True,
        #     text=True
        # )

        # running = False

        # return jsonify({
        #     "stdout": p.stdout,
        #     "stderr": p.stderr
        # })

    except:
        running = False
        err = traceback.format_exc()
        print(err)
        return "Something bad happened! Please inform the server admin\n" + err, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)