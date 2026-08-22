from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

# Je nach installierter Qiskit-Version
# wird hier eine passende Sampler-V2-Primitive verwendet.


# --------------------------------------------------
# Problem
# --------------------------------------------------

problem = QuadraticProgram("Investitionen")

problem.binary_var("A")
problem.binary_var("B")
problem.binary_var("C")


# Gewinn maximieren

problem.maximize(
    linear={
        "A": 9,
        "B": 7,
        "C": 4
    }
)


# Budgetbeschränkung

problem.linear_constraint(
    linear={
        "A": 4,
        "B": 3,
        "C": 2
    },
    sense="<=",
    rhs=7,
    name="Budget"
)


# --------------------------------------------------
# QAOA
# --------------------------------------------------

qaoa = QAOA(
    sampler=sampler,
    optimizer=COBYLA(maxiter=100),
    reps=2
)


# --------------------------------------------------
# High-Level Optimizer
# --------------------------------------------------

optimizer = MinimumEigenOptimizer(qaoa)


# --------------------------------------------------
# Lösen
# --------------------------------------------------

result = optimizer.solve(problem)


# --------------------------------------------------
# Ergebnis
# --------------------------------------------------

print(result.x)
print(result.fval)