from flask import Flask, request, jsonify
from flask_cors import CORS
import QuantumEngine.quantum_simulator as qsim
from QuantumEngine.utilities import validate_qasm
import API.info as info

app = Flask(__name__)
CORS(app)

qc = qsim.QuantumComputer(10)


# ----- Server Pinging and Info -----

@app.route("/")
def index():
    return info.HELP

@app.route("/ping")
def ping():
    return "Quantum Pi Online"


# ----- Running QASM Scripts -----

@app.route("/execute", methods=['POST'])
def run_script():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request contained no JSON body.'}), 400
    
    qasm = data.get('script')
    if not qasm:
        return jsonify({'error': 'No QASM script: Missing "script" field.'}), 400
    
    shots = data.get('shots')
    if not shots:
        shots = 1024
    
    try:
        result = qc(qasm, shots)
    except:
        return jsonify(validate_qasm(qasm, qc.num_qubits)), 400
    
    if result['statevector']:
        result['statevector'] = list(map(lambda z: (z.real, z.imag), result['statevector']))
    
    return jsonify(result), 200

@app.route("/validate", methods=['POST'])
def validate_script():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request contained no JSON body.'}), 400
    
    qasm = data.get('script')
    if not qasm:
        return jsonify({'error': 'No QASM script: Missing "script" field.'}), 400
    
    result = validate_qasm(qasm, qc.num_qubits)
    
    return jsonify(result), 200


# ----- Get Quantum Computer Properties -----

@app.route("/get/qubits")
def get_qubits():
    return jsonify({'message' : 'Success', 'num_qubits': qc.num_qubits}), 200

@app.route("/get/backend")
def get_backend():
    return jsonify({'message' : 'Success', 'backend': qc.backend}), 200


# ----- Update the Quantum Computer -----

@app.route("/update/qubits", methods=['POST'])
def update_qubits():
    data = request.get_json()
    
    if not data:
        return jsonify({'message' : 'Missing request body.', 'error': 'Request contained no JSON body.'}), 400
    
    num_qubits = int(data.get('num_qubits'))
    if not num_qubits:
        return jsonify({'message' : 'Missing request field.', 'error': 'Missing "num_qubits" field.'}), 400
    
    try:
        qc.num_qubits = num_qubits
    except ValueError as e:
        return jsonify({'message' : 'Invalid number of qubits.', 'error': e}), 400
    
    return jsonify({'message' : 'Success', 'num_qubits': num_qubits}), 200

@app.route("/update/backend", methods=['POST'])
def update_backend():
    data = request.get_json()
    
    if not data:
        return jsonify({'message' : 'Missing request body.', 'error': 'Request contained no JSON body.'}), 400
    
    backend = str(data.get('backend'))
    if not backend:
        return jsonify({'message' : 'Missing request field.', 'error': 'Missing "backend" field.'}), 400
    
    try:
        qc.backend = backend
    except ValueError as e:
        return jsonify({'message' : 'Invalid backend.', 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'message': 'Internal server error.', 'error': str(e)}), 500
    
    return jsonify({'message' : 'Success', 'backend': backend}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)