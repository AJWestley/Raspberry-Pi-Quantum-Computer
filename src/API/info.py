HELP = """
Quantum API - Usage Guide
==========================

Ping & Info
-----------
GET  /ping
    -> Returns a simple message confirming the server is online.

GET  /
    -> Displays this help information.

Quantum Script Execution
------------------------
POST /execute
    -> Execute a QASM script on the current quantum computer.
    Request JSON:
        {
            "script": "<str> QASM script (required)",
            "shots": <int> number of measurement repetitions (optional, default=1024)
        }
    Response JSON:
        {
            "counts": {str: int},
            "statevector": [(real, imag), ...]
        }

POST /validate
    -> Validate a QASM script without executing it.
    Request JSON:
        {
            "script": "<str> QASM script (required)"
        }
    Response JSON:
        {
            "valid": <bool>,
            "error": "<str>" (only if not valid)
        }

Quantum Computer Properties
---------------------------
GET /get/qubits
    -> Returns the number of qubits currently configured.

GET /get/backend
    -> Returns the currently selected backend.

Configuration / Update
----------------------
POST /update/qubits
    -> Update the number of qubits used by the simulator.
    Request JSON:
        {
            "num_qubits": <int> (required)
        }

POST /update/backend
    -> Change the quantum backend used for execution.
    Request JSON:
        {
            "backend": "<str>" (e.g., "noisy", "fault-tolerant") (required)
        }

Notes:
------
- All POST requests must include a valid JSON body with the required fields.
- Statevectors are returned as lists of (real, imag) tuples to ensure JSON compatibility.
- Ensure that QASM scripts are valid OpenQASM 2.0 code for correct execution and validation.

"""
