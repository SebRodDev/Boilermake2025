import networkx as nx
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.converters import QuadraticProgramToQubo

# Create a simple graph
G = nx.Graph()
G.add_edge(0, 1, weight=1)
G.add_edge(1, 2, weight=2)

# Create Maxcut instance and convert to QUBO
maxcut = Maxcut(G)
quadratic_program = maxcut.to_quadratic_program()
qubo = QuadraticProgramToQubo().convert(quadratic_program)

print(qubo) #verify that the qubo was created.