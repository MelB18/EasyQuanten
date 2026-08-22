# ============================================================
# RUCKSACKPROBLEM MIT QISKIT OPTIMIZATION
# ============================================================
#
# Ziel:
# Einen Rucksack mit maximal 7 kg möglichst wertvoll packen.
#
# Gegenstände:
#   Laptop  -> 4 kg, Wert 7
#   Kamera  -> 3 kg, Wert 6
#   Buch    -> 2 kg, Wert 4
#   Wasser  -> 1 kg, Wert 2
#
# x = 1 -> Gegenstand wird eingepackt
# x = 0 -> Gegenstand wird nicht eingepackt
# ============================================================


from qiskit_optimization import QuadraticProgram

from qiskit_optimization.algorithms import (
    MinimumEigenOptimizer
)

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler


# ============================================================
# 1. Daten
# ============================================================

items = {
    "Laptop": (4, 7),
    "Kamera": (3, 6),
    "Buch":   (2, 4),
    "Wasser": (1, 2),
}

capacity = 7


# ============================================================
# 2. QuadraticProgram erstellen
# ============================================================

problem = QuadraticProgram(
    name="Rucksackproblem"
)


# Für jeden Gegenstand eine binäre Variable erzeugen.
#
# Beispiel:
# Laptop = 1 -> Laptop wird genommen
# Laptop = 0 -> Laptop wird nicht genommen

for item in items:
    problem.binary_var(name=item)


# ============================================================
# 3. Zielfunktion
# ============================================================
#
# Wir wollen den Gesamtwert MAXIMIEREN.
#
# 7*Laptop + 6*Kamera + 4*Buch + 2*Wasser
#
# ============================================================

problem.maximize(
    linear={
        item: value
        for item, (weight, value) in items.items()
    }
)


# ============================================================
# 4. Nebenbedingung: maximales Gewicht
# ============================================================
#
# 4*Laptop + 3*Kamera + 2*Buch + 1*Wasser <= 7
#
# ============================================================

problem.linear_constraint(
    linear={
        item: weight
        for item, (weight, value) in items.items()
    },
    sense="<=",
    rhs=capacity,
    name="Gewicht"
)


# ============================================================
# 5. Problem anzeigen
# ============================================================

print("\nOptimierungsproblem:")
print(problem)


# ============================================================
# 6. QAOA konfigurieren
# ============================================================
#
# QAOA = Quantum Approximate Optimization Algorithm
#
# COBYLA optimiert die Parameter des QAOA-Schaltkreises.
#
# reps bestimmt die Anzahl der QAOA-Schichten.
# ============================================================

qaoa = QAOA(
    sampler=StatevectorSampler(),
    optimizer=COBYLA(maxiter=100),
    reps=2
)


# ============================================================
# 7. QAOA mit Qiskit Optimization verbinden
# ============================================================
#
# MinimumEigenOptimizer übernimmt die Verbindung zwischen
# dem mathematischen Optimierungsproblem und QAOA.
# ============================================================

optimizer = MinimumEigenOptimizer(qaoa)


# ============================================================
# 8. Optimierung starten
# ============================================================

result = optimizer.solve(problem)


# ============================================================
# 9. Ergebnis ausgeben
# ============================================================

print("\n" + "=" * 50)
print("ERGEBNIS")
print("=" * 50)

print("\nVariablen:")
print(result.x)


# ============================================================
# 10. Ausgewählte Gegenstände bestimmen
# ============================================================

total_weight = 0
total_value = 0

print("\nAusgewählte Gegenstände:")

for i, item in enumerate(items):

    # Ergebnis auf 0 oder 1 runden
    selected = round(result.x[i])

    if selected == 1:

        weight, value = items[item]

        print(
            f"  ✓ {item:8} "
            f"Gewicht: {weight} kg | "
            f"Wert: {value}"
        )

        total_weight += weight
        total_value += value


# ============================================================
# 11. Gesamtergebnis
# ============================================================

print("\n" + "-" * 50)

print(f"Gesamtgewicht: {total_weight} kg")
print(f"Gesamtwert:    {total_value}")
print(f"Kapazität:     {capacity} kg")

print("-" * 50)


if total_weight <= capacity:
    print("✓ Gewichtsbeschränkung eingehalten.")
else:
    print("✗ Gewichtsbeschränkung verletzt.")