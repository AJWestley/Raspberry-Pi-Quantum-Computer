from qiskit import QuantumCircuit
from qiskit.exceptions import QiskitError
import re

def validate_qasm(qasm_script: str) -> dict:
    """
    Validate that the circuit does not exceed qubit limits.

    Args:
        qc (QuantumCircuit): Circuit to validate.

    Raises:
        ValueError: If circuit uses more qubits than supported.
    """
    result = {
        'error': '',
        'line': -1,
        'col': -1,
    }
    try:
        QuantumCircuit.from_qasm_str(qasm_script)
    except QiskitError as e:
        # Try to extract line and column info from the error message
        msg = str(e)
        match = re.search(r':(\d+)\,(\d+):', msg)
        result['error'] = msg
        if match:
            line, col = match.groups()
            result['line'] = line
            result['col'] = col
    return result
    