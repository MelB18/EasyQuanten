# ============================================================
# QAOA – High-Level Qiskit
# Investitionsproblem mit 3 Projekten
# ============================================================

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler


# ============================================================
# 1. Projektdaten
# ============================================================

projects = {
    "A": {"cost": 4, "profit": 9},
    "B": {"cost": 3, "profit": 7},
    "C": {"cost": 2, "profit": 4},
}

budget = 7


# ============================================================
# 2. Optimierungsproblem
# ============================================================

problem = QuadraticProgram(
    name="Investitionsproblem"
)


# Für jedes Projekt eine Binärvariable:
#
# 0 = Projekt nicht auswählen
# 1 = Projekt auswählen

for project in projects:
    problem.binary_var(
        name=project
    )


# ============================================================
# 3. Zielfunktion
# ============================================================
#
# Maximiere den Gewinn.
#
# 9*A + 7*B + 4*C
#

problem.maximize(
    linear={
        project: data["profit"]
        for project, data in projects.items()
    }
)


# ============================================================
# 4. Budgetbeschränkung
# ============================================================
#
# 4*A + 3*B + 2*C <= 7
#

problem.linear_constraint(
    linear={
        project: data["cost"]
        for project, data in projects.items()
    },
    sense="<=",
    rhs=budget,
    name="Budget"
)


# ============================================================
# 5. Problem anzeigen
# ============================================================

print("Optimierungsproblem:")
print(problem)


# ============================================================
# 6. QAOA konfigurieren
# ============================================================

qaoa = QAOA(
    sampler=StatevectorSampler(),

    # Klassischer Optimierer für die QAOA-Parameter
    optimizer=COBYLA(
        maxiter=100
    ),

    # Anzahl der QAOA-Schichten
    reps=2
)


# ============================================================
# 7. High-Level Optimizer
# ============================================================
#
# MinimumEigenOptimizer verbindet:
#
# QuadraticProgram
#        +
#       QAOA
#
# ============================================================

optimizer = MinimumEigenOptimizer(
    qaoa
)


# ============================================================
# 8. Problem lösen
# ============================================================

result = optimizer.solve(
    problem
)


# ============================================================
# 9. Ergebnis
# ============================================================

print("\n" + "=" * 50)
print("ERGEBNIS")
print("=" * 50)

print("\nEntscheidungsvariablen:")

for project, value in zip(
    projects,
    result.x
):

    print(
        f"Projekt {project}: "
        f"{round(value)}"
    )


# ============================================================
# 10. Ausgewählte Projekte bestimmen
# ============================================================

selected = []

total_cost = 0
total_profit = 0


for project, value in zip(
    projects,
    result.x
):

    if round(value) == 1:

        selected.append(project)

        total_cost += projects[project]["cost"]
        total_profit += projects[project]["profit"]


# ============================================================
# 11. Zusammenfassung
# ============================================================

print("\nAusgewählte Projekte:")

for project in selected:
    print(
        f"  ✓ Projekt {project}"
    )

print("\nGesamtkosten:",
      total_cost,
      "Mio. €")

print("Gesamtgewinn:",
      total_profit)

print("Budget:",
      budget,
      "Mio. €")


# ============================================================
# 12. Ergebnis überprüfen
# ============================================================

if total_cost <= budget:

    print(
        "\n✓ Budget eingehalten."
    )

else:

    print(
        "\n✗ Budget überschritten."
    )