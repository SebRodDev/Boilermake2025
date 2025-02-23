import json
import networkx as nx
import numpy as np
import openai
import pandas as pd

from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Sampler  # new primitive interface for simulation
from qiskit.quantum_info import SparsePauliOp

# Define the identity and Pauli-Z operators (for single qubit)
I_single = SparsePauliOp("I")
Z_single = SparsePauliOp("Z")

def load_students(filename):
    """
    Loads student records from a Parquet file.
    Each record has fields like:
    "student_id", "course_name", "failure_prob", "weakest_area", etc.
    """
    students = pd.read_parquet(filename).to_dict(orient='records')
    return students

def build_graph(students):
    """
    Constructs a graph where:
      - Each node represents a student (using student_id).
      - An edge is added between every pair of students.
      - Edge weight is 1.0 if students share the same 'weakest_area' and 0.1 otherwise.
    """
    G = nx.Graph()
    for student in students:
        student_id = student["student_id"]
        G.add_node(student_id, **student)
    
    student_ids = list(G.nodes)
    for i in range(len(student_ids)):
        for j in range(i+1, len(student_ids)):
            s1 = G.nodes[student_ids[i]]
            s2 = G.nodes[student_ids[j]]
            weight = 1.0 if s1["weakest_area"] == s2["weakest_area"] else 0.1
            G.add_edge(student_ids[i], student_ids[j], weight=weight)
    return G

def get_maxcut_operator(G):
    """
    Returns the cost operator for the MAXCUT problem on graph G.
    For each edge (i, j) with weight w, the term is:
        (w/2) * (I - Z_i Z_j)
    The overall cost operator is the sum over all edges.
    """
    n = len(G.nodes)
    nodes = list(G.nodes)
    # Initialize the cost operator as the zero operator
    cost_op = SparsePauliOp.from_list([("I"*n, 0.0)])
    
    # Loop over each edge in the graph
    for i in range(n):
        for j in range(i+1, n):
            if G.has_edge(nodes[i], nodes[j]):
                weight = G[nodes[i]][nodes[j]]["weight"]
                # Build a pauli string with I everywhere except Z at positions i and j
                pauli_list = ["I"] * n
                pauli_list[i] = "Z"
                pauli_list[j] = "Z"
                pauli_label = "".join(pauli_list)
                # Construct the term: (w/2)*(I - Z_i Z_j)
                ident_op = SparsePauliOp.from_list([("I"*n, 1.0)])
                zz_op = SparsePauliOp.from_list([(pauli_label, 1.0)])
                term = 0.5 * weight * (ident_op - zz_op)
                cost_op = cost_op + term
    return cost_op

def run_qaoa(G):
    """
    Sets up and runs QAOA for the MAXCUT instance defined by graph G.
    Returns the QAOA result.
    """
    n = len(G.nodes)
    cost_operator = get_maxcut_operator(G)
    
    optimizer = COBYLA(maxiter=250)
    simulator = AerSimulator()
    
    # With the new primitive interface, you might use Sampler for measurement.
    sampler = Sampler(backend=simulator)
    
    # Configure QAOA with 1 repetition (layer)
    qaoa = QAOA(optimizer=optimizer, reps=1, sampler=sampler)
    
    result = qaoa.compute_minimum_eigenvalue(operator=cost_operator)
    
    print("Optimal (minimum) cost value:", result.eigenvalue.real)
    print("QAOA raw state (amplitudes):")
    print(result.eigenstate)
    
    return result

def interpret_qaoa_result(result, nodes):
    """
    Extracts the most-probable bitstring from the QAOA result,
    maps it to student groups, and uses an AI assistant (via OpenAI)
    to provide an interpretation.
    """
    # Assume the QAOA eigenstate is a state vector (numpy array)
    state_vector = np.array(result.eigenstate)
    probabilities = np.abs(state_vector)**2
    best_index = np.argmax(probabilities)
    n = len(nodes)
    # Convert index to bitstring with leading zeros
    best_bitstring = format(best_index, f"0{n}b")
    
    # Create groups based on bitstring assignment (0: Group A, 1: Group B)
    groups = {"Group A": [], "Group B": []}
    for i, bit in enumerate(best_bitstring):
        if bit == "0":
            groups["Group A"].append(nodes[i])
        else:
            groups["Group B"].append(nodes[i])
    
    # Prepare a prompt for the AI assistant.
    prompt = (
        f"The QAOA optimization resulted in the bitstring: {best_bitstring}.\n"
        f"This implies the following student grouping based on the node ordering:\n{json.dumps(groups, indent=2)}\n\n"
        "Please interpret these results. What insights can be drawn regarding how the students are grouped "
        "for tutoring, and what recommendations could be made to further optimize tutor group formation?"
    )
    
    # Set your OpenAI API key (replace 'YOUR_API_KEY' with your actual key)
    openai.api_key = ""
    response = openai.ChatCompletion.create(
       model="gpt-4o",
       messages=[
           {"role": "system", "content": "You are a helpful AI assistant for data analysis."},
           {"role": "user", "content": prompt}
       ]
    )
    interpretation = response.choices[0].message["content"]
    return best_bitstring, groups, interpretation

def save_interpretation_to_file(best_bitstring, groups, interpretation, filename="interpreted_result.txt"):
    """
    Saves the QAOA result interpretation and grouping details into a text file.
    """
    with open(filename, "w") as f:
        f.write("QAOA Result Interpretation\n")
        f.write("==========================\n")
        f.write(f"Best Bitstring: {best_bitstring}\n\n")
        f.write("Student Groups:\n")
        f.write(json.dumps(groups, indent=2))
        f.write("\n\nInterpretation by AI Assistant:\n")
        f.write(interpretation)
    print(f"Interpretation saved to {filename}")

if __name__ == "__main__":
    # Step 1: Load student data and build the relation graph.
    students = load_students("risks_week10.parquet")
    G = build_graph(students)
    
    # Step 2: Run QAOA to solve the MAXCUT problem.
    result = run_qaoa(G)
    nodes = list(G.nodes)
    
    # Step 3: Interpret the QAOA result using the AI assistant.
    best_bitstring, groups, interpretation = interpret_qaoa_result(result, nodes)
    
    # Step 4: Save the interpretation to a new file.
    save_interpretation_to_file(best_bitstring, groups, interpretation)
