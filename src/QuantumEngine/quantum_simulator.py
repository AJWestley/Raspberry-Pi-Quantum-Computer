from typing import Literal
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import Aer, AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeAlmadenV2

BACKEND = Literal['fault-tolerant', 'noisy']
FAULT_TOLERANT_BACKEND = lambda: "aer_simulator"
NOISY_BACKEND = lambda: FakeAlmadenV2()

class QuantumComputer:
    """
    QuantumComputer simulates quantum circuit execution on either a fault-tolerant 
    or noisy backend.

    Attributes:
        num_qubits (int): Maximum qubits supported.
        backend (Literal['fault-tolerant', 'noisy']): Type of backend simulator.
    """
    
    ALLOWED_BACKENDS = ('fault-tolerant', 'noisy')
    
    def __init__(self, num_qubits: int, backend: BACKEND = 'fault-tolerant', max_qubits: int = 0):
        """
        Initialize the QuantumComputer with a specified number of qubits and backend.

        Args:
            num_qubits (int): Maximum number of qubits this instance can handle.
            backend (Literal['fault-tolerant', 'noisy'], optional): Backend type. Defaults to 'fault-tolerant'.

        Raises:
            ValueError: If num_qubits is less than 1.
            ValueError: If backend value is invalid.
        """
        if max_qubits < 0:
            raise ValueError("max_qubits must be a non-negative integer.")
        self.__max_qubits = max_qubits
        self.__simulators: dict = {}
        self.backend = backend
        self.num_qubits = num_qubits
    
    def run(self, qasm_script: str, shots: int = 1024) -> dict:
        """
        Execute a QASM script on the selected backend.

        Args:
            qasm_script (str): Quantum circuit in QASM format.
            shots (int, optional): Number of circuit executions for measurement statistics. Defaults to 1024.

        Returns:
            dict: Dictionary containing statevector (list of complex amplitudes),
                                        probabilities (dict of basis states to probabilities),
                                        and counts (measurement results).
        """
        return self(qasm_script, shots)
    
    def __repr__(self) -> str:
        """Return string representation of the QuantumComputer instance."""
        return f"QuantumComputer(num_qubits={self.num_qubits}, backend='{self.backend}')"
    
    def __len__(self) -> int:
        """Return the number of qubits supported."""
        return self.num_qubits
    
    def __call__(self, qasm_script: str, shots: int = 1024) -> dict:
        """
        Execute a QASM script on the selected backend.

        Args:
            qasm_script (str): Quantum circuit in QASM format.
            shots (int, optional): Number of circuit executions for measurement statistics. Defaults to 1024.

        Returns:
            dict: Dictionary containing statevector (list of complex amplitudes),
                                        probabilities (dict of basis states to probabilities),
                                        and counts (measurement results).
        """
        if self.backend not in self.__simulators:
            self.__init_backend(self.backend)
        sim = self.__simulators[self.backend]

        qc = QuantumCircuit.from_qasm_str(qasm_script)
        self.__validate_circuit(qc)

        qc_clean = qc.remove_final_measurements(inplace=False)
        state = Statevector.from_instruction(qc_clean)
        probabilities = state.probabilities_dict()

        qc_compiled = transpile(qc, backend=sim)
        result = sim.run(qc_compiled, shots=shots).result()

        return {
            "statevector": list(state.data),
            "probabilities": probabilities,
            "counts": result.get_counts()
        }
    
    @property
    def backend(self) -> BACKEND:
        """Backend property getter."""
        return self.__backend
    
    @backend.setter
    def backend(self, value: BACKEND) -> None:
        """
        Backend property setter with validation.

        Args:
            value (BACKEND): New backend value.

        Raises:
            ValueError: If backend value is invalid.
        """
        if value not in QuantumComputer.ALLOWED_BACKENDS:
            raise ValueError(f'The provided backend ({value}) is invalid. Allowed values: {QuantumComputer.ALLOWED_BACKENDS}')
        self.__backend = value
    
    @property
    def num_qubits(self) -> int:
        """Number of qubits property getter."""
        return self.__n_qubits
    
    @num_qubits.setter
    def num_qubits(self, n: int) -> None:
        """
        Number of qubits property setter with validation.

        Args:
            n (int): Number of qubits.

        Raises:
            ValueError: If n is less than 1.
        """
        if n <= 0:
            raise ValueError(f'Invalid num_qubits: {n}. Only integers >= 1 are valid.')
        if self.__max_qubits:
            if n > self.__max_qubits:
                raise ValueError(f'This quantum computer cannot support more than {self.__max_qubits} qubits.')
        self.__n_qubits = n
    
    def __init_backend(self, backend: BACKEND) -> None:
        """
        Initialize the backend simulator.

        Args:
            backend (BACKEND): Backend type to initialize.
        """
        if backend == 'fault-tolerant':
            self.__simulators[backend] = Aer.get_backend(FAULT_TOLERANT_BACKEND())
        elif backend == 'noisy':
            self.__simulators[backend] = AerSimulator.from_backend(NOISY_BACKEND())
    
    def __validate_circuit(self, qc: QuantumCircuit) -> None:
        """
        Validate that the circuit does not exceed qubit limits.

        Args:
            qc (QuantumCircuit): Circuit to validate.

        Raises:
            ValueError: If circuit uses more qubits than supported.
        """
        if qc.num_qubits > self.num_qubits:
            raise ValueError(f"QASM circuit uses {qc.num_qubits} qubits, which exceeds this QuantumComputer's limit of {self.num_qubits}")
    