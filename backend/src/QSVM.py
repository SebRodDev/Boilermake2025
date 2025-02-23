import pennylane as qml
import numpy as np
from sklearn.svm import SVC
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import json

# --------------------------
# Part 1: Define Quantum Feature Map & Kernel in PennyLane
# --------------------------
# Use PennyLane's default.qubit simulator (fast and efficient)
n_wires = 2
dev = qml.device("default.qubit", wires=n_wires)

@qml.qnode(dev)
def feature_map(x):
    # Use a simple embedding: encode each feature into a rotation angle
    qml.AngleEmbedding(x, wires=range(n_wires))
    # Introduce entanglement
    qml.CNOT(wires=[0, 1])
    qml.RZ(np.pi / 4, wires=1)
    return qml.state()

def quantum_kernel(x1, x2):
    # Compute state vectors for both inputs
    psi1 = feature_map(x1)
    psi2 = feature_map(x2)
    # The kernel is the squared magnitude of the inner product
    return np.abs(np.vdot(psi1, psi2))**2

# --------------------------
# Part 2: Build Kernel Matrix and Train SVM
# --------------------------
# Generate a toy two-class dataset with 2 features
X, y = make_classification(n_samples=100, n_features=2, 
                           n_informative=2, n_redundant=0, 
                           random_state=42)
# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42)

# Compute the quantum kernel matrix for training data
def compute_kernel_matrix(X1, X2):
    n1 = X1.shape[0]
    n2 = X2.shape[0]
    K = np.zeros((n1, n2))
    for i in range(n1):
        for j in range(n2):
            K[i, j] = quantum_kernel(X1[i], X2[j])
    return K

# Compute training and testing kernel matrices
K_train = compute_kernel_matrix(X_train, X_train)
K_test = compute_kernel_matrix(X_test, X_train)  # note: test vs training

# Train an SVM classifier using the precomputed kernel
svm = SVC(kernel="precomputed")
svm.fit(K_train, y_train)

# Make predictions and evaluate accuracy
y_pred = svm.predict(K_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test Accuracy:", accuracy)

# Generate a classification report
report_text = classification_report(y_test, y_pred)
report_dict = classification_report(y_test, y_pred, output_dict=True)

# Save raw report to a JSON file
with open("svm_results_pennylane.json", "w") as f:
    json.dump(report_dict, f, indent=2)

# --------------------------
# Part 3: Use AI (Transformer) to Interpret Results
# --------------------------
from transformers import pipeline

# Create a summarization pipeline (this may download a model on first run)
summarizer = pipeline("summarization")

input_text = (
    "PennyLane Quantum Kernel SVM Classification Report:\n" + report_text +
    "\nInterpret the performance of this quantum-enhanced classifier and discuss the "
    "implications of the quantum kernel in capturing data relationships."
)

# Summarize the report (adjust max_length/min_length as needed)
interpretation = summarizer(input_text, max_length=150, min_length=50, do_sample=False)
interpretation_text = interpretation[0]['summary_text']
print("\nAI Interpretation:\n", interpretation_text)

# Store the AI interpretation to a text file
with open("results_interpretation_pennylane.txt", "w") as f:
    f.write(interpretation_text)

# --------------------------
# Part 4: Visualize and Save Decision Boundary
# --------------------------
# Create a grid over feature space
xx, yy = np.meshgrid(np.linspace(X[:,0].min()-1, X[:,0].max()+1, 100),
                     np.linspace(X[:,1].min()-1, X[:,1].max()+1, 100))
grid = np.c_[xx.ravel(), yy.ravel()]

# Compute kernel matrix for grid vs training set and predict labels
K_grid = compute_kernel_matrix(grid, X_train)
Z = svm.predict(K_grid)
Z = Z.reshape(xx.shape)

plt.figure(figsize=(8, 6))
plt.contourf(xx, yy, Z, alpha=0.4, cmap='coolwarm')
plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, marker='o', edgecolors='k', label='Train')
plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test, marker='x', label='Test')
plt.title("PennyLane Quantum Kernel SVM Decision Boundary")
plt.legend()
plt.savefig("decision_boundary_pennylane.png")
plt.show()
