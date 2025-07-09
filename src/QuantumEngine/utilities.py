from qiskit import QuantumCircuit
from qiskit.exceptions import QiskitError
import re

VALID = -1
TOO_MANY_QUBITS = -2
REGISTER_MISMATCH = -3
INTERMEDIATE_MEASUREMENT = -4
NO_MEASUREMENT = -5
UNKNOWN_ERROR = -6

def validate_qasm(qasm_script: str, num_qubits: int) -> dict:
    """
    Validate that the circuit does not exceed qubit limits.

    Args:
        qc (QuantumCircuit): Circuit to validate.

    Raises:
        ValueError: If circuit uses more qubits than supported.
    """
    result = {
        'error': 'Valid circuit.',
        'line': VALID,
        'col': VALID,
    }
    try:
        qc = QuantumCircuit.from_qasm_str(qasm_script)
        
        if qc.num_qubits > num_qubits:
            result['line'] = TOO_MANY_QUBITS
            result['col'] = TOO_MANY_QUBITS
            result['error'] = f'The device cannot support more than {num_qubits} qubits.'
        elif qc.num_qubits != qc.num_clbits:
            result['line'] = REGISTER_MISMATCH
            result['col'] = REGISTER_MISMATCH
            result['error'] = f'The number of qubits ({qc.num_qubits}) should match the number of classical registers ({qc.num_clbits}).'
        elif has_intermediate_measurement(qasm_script):
            result['line'] = INTERMEDIATE_MEASUREMENT
            result['col'] = INTERMEDIATE_MEASUREMENT
            result['error'] = f'Cannot measure in the middle of a circuit.'
        elif not has_measurement(qasm_script):
            result['line'] = NO_MEASUREMENT
            result['col'] = NO_MEASUREMENT
            result['error'] = f'Circuit must contain at least one measurement.'
        
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

def has_intermediate_measure(qasm_code):
    lines = qasm_code.strip().splitlines()
    found_measure_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue

        is_measure = re.match(r'^measure\s+[^\n]+;\s*$', stripped)

        if is_measure:
            found_measure_block = True
        elif found_measure_block:
            return True

    return False

def has_measurement(qasm_script: str):
    return bool(re.search(r'^\s*measure\s+.+?;\s*$', qasm_script, re.MULTILINE))