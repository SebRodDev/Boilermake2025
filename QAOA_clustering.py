import pandas as pd
import rustworkx as rx
import numpy as np
from itertools import combinations
from sklearn.preprocessing import StandardScaler
from qiskit.primitives import Sampler, Estimator
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.quantum_info import Pauli, SparsePauliOp
from qiskit.algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Options
from qiskit.transpiler import PassManager

def create_hamiltonian(graph):
    """Create the problem Hamiltonian for the QAOA circuit."""
    num_nodes = len(graph.node_indices())
    hamiltonian_terms = []
    coefficients = []
    
    # Add terms for each edge in the graph
    for edge in graph.edge_list():
        i, j, weight = edge
        # Create Pauli string for edge interaction
        pauli_str = ['I'] * num_nodes
        pauli_str[i] = 'Z'
        pauli_str[j] = 'Z'
        hamiltonian_terms.append(''.join(pauli_str))
        coefficients.append(weight)
    
    # Convert to SparsePauliOp
    if not hamiltonian_terms:  # Handle empty graph case
        pauli_str = ['I'] * num_nodes
        return SparsePauliOp(''.join(pauli_str))
        
    return SparsePauliOp(hamiltonian_terms, coefficients)

def create_mixer_hamiltonian(num_qubits):
    """Create the mixer Hamiltonian for the QAOA circuit."""
    mixer_terms = []
    coefficients = []
    
    # Add X terms for each qubit
    for i in range(num_qubits):
        pauli_str = ['I'] * num_qubits
        pauli_str[i] = 'X'
        mixer_terms.append(''.join(pauli_str))
        coefficients.append(1.0)
        
    return SparsePauliOp(mixer_terms, coefficients)

def initialize_service(token, channel="ibm_quantum"):
    """Initialize the IBM Quantum service with the provided token."""
    return QiskitRuntimeService(channel=channel, token=token)

def load_data(filepath="risks_week10.parquet"):
    """Load and preprocess student data."""
    data = pd.read_parquet(filepath, columns=['student_id', 'course_name', 'area_score'])
    data = data.dropna(subset=['area_score'])
    data['student_id'] = data['student_id'].astype(str)
    data['course_name'] = data['course_name'].astype(str)
    
    # Aggregate and scale the scores
    students = data.groupby(['student_id', 'course_name']).area_score.mean().reset_index()
    students['area_score_scaled'] = StandardScaler().fit_transform(students[['area_score']])
    return students

def build_graph(students, edge_threshold=0.2):
    """Build a graph representing student relationships based on scores."""
    G = rx.PyGraph()
    node_map = {}
    
    # Add nodes (students)
    for idx, row in students.iterrows():
        node_id = G.add_node({
            'student_id': row['student_id'],
            'course': row['course_name'],
            'score': row['area_score_scaled']
        })
        node_map[node_id] = (row['student_id'], row['course_name'])
    
    # Add edges between students in the same course with similar scores
    for course, group in students.groupby('course_name'):
        if len(group) < 2:
            continue
        indices = group.index.tolist()
        for i, j in combinations(indices, 2):
            diff = abs(group.loc[i, 'area_score_scaled'] - group.loc[j, 'area_score_scaled'])
            weight = max(0, 1 - diff)
            if weight > edge_threshold:
                G.add_edge(i, j, weight)
    
    return G, node_map

def create_qaoa_circuit(num_qubits, reps):
    """Create a QAOA circuit with the specified number of qubits and repetitions."""
    params = ParameterVector('θ', 2 * reps)
    
    # Initialize circuit
    qc = QuantumCircuit(num_qubits)
    
    # Initial state preparation (Hadamard gates)
    for qubit in range(num_qubits):
        qc.h(qubit)
    
    # QAOA layers
    for p in range(reps):
        # Problem unitary
        for i in range(num_qubits):
            qc.rz(params[2*p], i)
        
        # Mixer unitary
        for i in range(num_qubits):
            qc.rx(params[2*p + 1], i)
    
    # Measurements
    qc.measure_all()
    
    return qc

def build_cost_hamiltonian(graph: rx.PyGraph):
    """Build the cost Hamiltonian for the Max-Cut problem."""
    pauli_list = []
    for edge in graph.edge_list():
        # Create Pauli string for each edge
        op = ["I"] * graph.num_nodes()
        op[edge[0]] = "Z"
        op[edge[1]] = "Z"
        weight = graph.get_edge_data(edge[0], edge[1])
        pauli_list.append((Pauli("".join(op)), weight))
    
    return SparsePauliOp.from_list(pauli_list)

def optimize_qaoa(circuit, cost_ham, service, backend_name, reps):
    """Optimize QAOA parameters using the Estimator primitive."""
    options = Options()
    options.resilience_level = 1
    options.optimization_level = 1
    
    with Session(service=service, backend=backend_name) as session:
        estimator = Estimator(session=session, options=options)
        
        def objective(params):
            result = estimator.run(
                circuits=[circuit],
                observables=[cost_ham],
                parameter_values=[params]
            ).result()
            return result.values[0]
        
        # Initialize optimizer
        optimizer = COBYLA(maxiter=100, tol=1e-2)
        initial_params = np.random.uniform(0, 2*np.pi, 2 * reps)
        
        result = optimizer.minimize(
            fun=objective,
            x0=initial_params
        )
        
        return result.x

def sample_solution(circuit, optimal_params, service, backend_name):
    """Sample from the optimized circuit using the Sampler primitive."""
    options = Options()
    options.shots = 10000
    options.optimization_level = 1
    
    with Session(service=service, backend=backend_name) as session:
        sampler = Sampler(session=session, options=options)
        bound_circuit = circuit.bind_parameters(optimal_params)
        result = sampler.run(circuits=[bound_circuit]).result()
        counts = result.quasi_dists[0]
        
        return {format(k, f'0{circuit.num_qubits}b'): v 
                for k, v in counts.items()}

def main():
    # Initialize IBM Quantum service
    token = "03c81e2cd8d9f136c4e278b0ddb2cf79b4d21d9d4167c198ea24bc1174f6c77fd2f373ec8e36dd4ab679fbaed65fb7470621bbdfd6194973270ed974c340c30b"  # Replace with your token
    service = initialize_service(token)
    backend_name = "ibm_brisbane"  # Or another available backend
    
    # Load and process data
    students = load_data()
    graph, node_map = build_graph(students)
    print(f"Graph created with {graph.num_nodes()} nodes and {graph.num_edges()} edges")
    
    # Create QAOA circuit
    num_qubits = graph.num_nodes()
    reps = 2  # Number of QAOA repetitions
    circuit = create_qaoa_circuit(num_qubits, reps)
    
    # Build cost Hamiltonian
    cost_ham = build_cost_hamiltonian(graph)
    
    # Optimize QAOA parameters
    print("Optimizing QAOA parameters...")
    optimal_params = optimize_qaoa(circuit, cost_ham, service, backend_name, reps)
    
    # Sample from optimized circuit
    print("Sampling from optimized circuit...")
    counts = sample_solution(circuit, optimal_params, service, backend_name)
    
    # Process results
    partition = {}
    for bitstr, prob in counts.items():
        if prob > 0.01:  # Filter out low-probability states
            for i in range(graph.num_nodes()):
                group = int(bitstr[i])
                partition[node_map[i]] = group
    
    # Print results
    print("\nTutor Group Assignments:")
    for (student_id, course), group in partition.items():
        print(f"Student {student_id} in {course}: Group {group}")

if __name__ == "__main__":
    main()