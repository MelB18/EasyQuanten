# ============================================================
# QAOA + SamplerV2 + Qiskit Optimization
#
# Reales Beispiel:
# Auswahl von 3 Investitionsprojekten
# ============================================================

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA

# Moderne SamplerV2-Primitive von Qiskit Aer
from qiskit_aer.primitives import SamplerV2


# ============================================================
# 1. PROBLEM DEFINIEREN
# ============================================================

problem = QuadraticProgram(
    name="Investitionsproblem"
)


# ------------------------------------------------------------
# Binäre Entscheidungsvariablen
#
# 0 = Projekt nicht auswählen
# 1 = Projekt auswählen
# ------------------------------------------------------------

problem.binary_var("A")
problem.binary_var("B")
problem.binary_var("C")


# ============================================================
# 2. ZIELFUNKTION
# ============================================================
#
# Gewinn:
#
# A -> 9
# B -> 7
# C -> 4
#
# Wir wollen den Gewinn maximieren.
# ============================================================

problem.maximize(
    linear={
        "A": 9,
        "B": 7,
        "C": 4
    }
)


# ============================================================
# 3. BUDGET-BESCHRÄNKUNG
# ============================================================
#
# Kosten:
#
# A -> 4
# B -> 3
# C -> 2
#
# Maximal 7 Mio. €
# ============================================================

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


# ============================================================
# 4. PROBLEM ANZEIGEN
# ============================================================

print("=" * 60)
print("OPTIMIERUNGSPROBLEM")
print("=" * 60)

print(problem)


# ============================================================
# 5. SAMPLER V2 ERZEUGEN
# ============================================================
#
# SamplerV2 ist die moderne Primitive zum Sampling von
# Quantenschaltkreisen.
#
# Wir verwenden hier den lokalen Qiskit-Aer-Simulator.
#
# Dadurch benötigen wir keinen echten Quantencomputer.
# ============================================================

sampler = SamplerV2()


# ============================================================
# 6. QAOA ERSTELLEN
# ============================================================
#
# QAOA benötigt:
#
#   sampler
#   klassischer Optimierer
#   Anzahl der QAOA-Schichten
#
# ============================================================

qaoa = QAOA(
    sampler=sampler,

    # Klassischer Optimierer
    optimizer=COBYLA(
        maxiter=100
    ),

    # Anzahl der QAOA-Schichten
    reps=2
)


# ============================================================
# 7. HIGH-LEVEL OPTIMIZER
# ============================================================
#
# MinimumEigenOptimizer verbindet unser
# QuadraticProgram mit QAOA.
#
# Qiskit übernimmt dabei die notwendige Umwandlung
# des Optimierungsproblems.
# ============================================================

optimizer = MinimumEigenOptimizer(
    qaoa
)


# ============================================================
# 8. OPTIMIERUNG AUSFÜHREN
# ============================================================

result = optimizer.solve(
    problem
)


# ============================================================
# 9. ERGEBNIS AUSGEBEN
# ============================================================

print("\n")
print("=" * 60)
print("ERGEBNIS")
print("=" * 60)

print("\nEntscheidungen:")

for name, value in zip(
    ["A", "B", "C"],
    result.x
):

    print(
        f"Projekt {name}: "
        f"{round(value)}"
    )


# ============================================================
# 10. AUSGEWÄHLTE PROJEKTE
# ============================================================

projects = {
    "A": {
        "cost": 4,
        "profit": 9
    },

    "B": {
        "cost": 3,
        "profit": 7
    },

    "C": {
        "cost": 2,
        "profit": 4
    }
}


selected = []

total_cost = 0
total_profit = 0


for name, value in zip(
    projects,
    result.x
):

    if round(value) == 1:

        selected.append(name)

        total_cost += projects[name]["cost"]

        total_profit += projects[name]["profit"]


# ============================================================
# 11. ZUSAMMENFASSUNG
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
      7,
      "Mio. €")


# ============================================================
# 12. OPTIMALITÄT PRÜFEN
# ============================================================

if total_cost <= 7:

    print(
        "\n✓ Budget eingehalten."
    )

else:

    print(
        "\n✗ Budget überschritten."
    )


if total_profit == 16:

    print(
        "✓ Optimale Lösung gefunden."
    )

else:

    print(
        "⚠ Nicht das bekannte Optimum."
    )