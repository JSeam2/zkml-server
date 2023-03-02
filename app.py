from flask import Flask, request
import os
from werkzeug.utils import secure_filename


app = Flask("ZKML-server")

"""
Simple single session prover
"""
@app.route('/')
def index():
    return "Welcome to the ZKML-server"

"""
Upload files for proving
"""
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # save the single onnx file
        onnx = request.files['onnx']
        inputJson = request.files['inputJson']
        onnx.save(os.path.join("uploads", secure_filename(onnx.filename)))
        inputJson.save(os.path.join("uploads", secure_filename(inputJson.filename)))

        return "Successfully uploaded"


"""
Generate EVM Proof and sends proof.pf and proof.vk to user
"""
@app.route('/gen_evm_proof', methods=['POST'])
def gen_evm_proof():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)