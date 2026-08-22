# ============================================================
# RUCKSACKPROBLEM
# Vergleich:
#   1. Klassische exakte Optimierung
#   2. QAOA (Quantenoptimierung)
# ============================================================

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler

from qiskit_algorithms import NumPyMinimumEigensolver


# ============================================================
# 1. PROBLEMDATEN
# ============================================================

items = {
    "Laptop": {"weight": 4, "value": 7},
    "Kamera": {"weight": 3, "value": 6},
    "Buch":   {"weight": 2, "value": 4},
    "Wasser": {"weight": 1, "value": 2},
}

capacity = 7


# ============================================================
# 2. OPTIMIERUNGSPROBLEM ERSTELLEN
# ============================================================

problem = QuadraticProgram(
    name="Rucksackproblem"
)


# Für jeden Gegenstand eine Binärvariable.
#
# 1 = Gegenstand wird genommen
# 0 = Gegenstand wird nicht genommen

for item in items:
    problem.binary_var(name=item)


# ============================================================
# 3. ZIELFUNKTION
# ============================================================
#
# Wir wollen den Gesamtwert maximieren.
#
# Laptop  -> +7
# Kamera  -> +6
# Buch    -> +4
# Wasser  -> +2
#
# ============================================================

problem.maximize(
    linear={
        item: data["value"]
        for item, data in items.items()
    }
)


# ============================================================
# 4. GEWICHTSBESCHRÄNKUNG
# ============================================================
#
# Das Gesamtgewicht darf maximal 7 kg sein.
#
# 4*Laptop + 3*Kamera + 2*Buch + 1*Wasser <= 7
#
# ============================================================

problem.linear_constraint(
    linear={
        item: data["weight"]
        for item, data in items.items()
    },
    sense="<=",
    rhs=capacity,
    name="Gewicht"
)


# ============================================================
# 5. PROBLEM ANZEIGEN
# ============================================================

print("=" * 65)
print("RUCKSACKPROBLEM – KLASSISCH VS. QAOA")
print("=" * 65)

print("\nProblem:")
print(problem)


# ============================================================
# 6. KLASSISCHE EXAKTE LÖSUNG
# ============================================================
#
# NumPyMinimumEigensolver durchsucht das Problem exakt.
#
# Das Ergebnis verwenden wir als Referenz:
#
# "Was ist die tatsächlich optimale Lösung?"
#
# ============================================================

exact_solver = NumPyMinimumEigensolver()

classical_optimizer = MinimumEigenOptimizer(
    exact_solver
)

classical_result = classical_optimizer.solve(
    problem
)


# ============================================================
# 7. QAOA KONFIGURIEREN
# ============================================================
#
# QAOA ist ein hybrider Quantenalgorithmus:
#
# Quantencomputer:
#   Bewertung von Quantenzuständen
#
# Klassischer Computer:
#   Optimierung der QAOA-Parameter
#
# ============================================================

qaoa = QAOA(
    sampler=StatevectorSampler(),

    # COBYLA optimiert die QAOA-Parameter
    optimizer=COBYLA(
        maxiter=100
    ),

    # Anzahl der QAOA-Schichten
    reps=2
)


# ============================================================
# 8. QAOA MIT QISKIT OPTIMIZATION VERBINDEN
# ============================================================

qaoa_optimizer = MinimumEigenOptimizer(
    qaoa
)


# ============================================================
# 9. QAOA AUSFÜHREN
# ============================================================

qaoa_result = qaoa_optimizer.solve(
    problem
)


# ============================================================
# 10. HILFSFUNKTION ZUR ERGEBNISAUSWERTUNG
# ============================================================

def evaluate_solution(result):
    """
    Ermittelt aus einer Qiskit-Lösung:

    - ausgewählte Gegenstände
    - Gesamtgewicht
    - Gesamtwert
    """

    selected_items = []

    total_weight = 0
    total_value = 0

    for i, item in enumerate(items):

        # Qiskit liefert Werte wie 0 oder 1.
        selected = round(result.x[i])

        if selected == 1:

            selected_items.append(item)

            total_weight += items[item]["weight"]
            total_value += items[item]["value"]

    return (
        selected_items,
        total_weight,
        total_value
    )


# ============================================================
# 11. KLASSISCHE LÖSUNG AUSWERTEN
# ============================================================

classical_items, classical_weight, classical_value = (
    evaluate_solution(classical_result)
)


# ============================================================
# 12. QAOA-LÖSUNG AUSWERTEN
# ============================================================

qaoa_items, qaoa_weight, qaoa_value = (
    evaluate_solution(qaoa_result)
)


# ============================================================
# 13. KLASSISCHES ERGEBNIS AUSGEBEN
# ============================================================

print("\n")
print("=" * 65)
print("KLASSISCHE EXAKTE LÖSUNG")
print("=" * 65)

print("\nAusgewählte Gegenstände:")

for item in classical_items:
    print(
        f"  ✓ {item:8} "
        f"{items[item]['weight']} kg | "
        f"Wert {items[item]['value']}"
    )

print("\nGesamtgewicht:", classical_weight, "kg")
print("Gesamtwert:   ", classical_value)


# ============================================================
# 14. QAOA-ERGEBNIS AUSGEBEN
# ============================================================

print("\n")
print("=" * 65)
print("QAOA-LÖSUNG")
print("=" * 65)

print("\nAusgewählte Gegenstände:")

for item in qaoa_items:
    print(
        f"  ✓ {item:8} "
        f"{items[item]['weight']} kg | "
        f"Wert {items[item]['value']}"
    )

print("\nGesamtgewicht:", qaoa_weight, "kg")
print("Gesamtwert:   ", qaoa_value)


# ============================================================
# 15. VERGLEICH
# ============================================================

print("\n")
print("=" * 65)
print("VERGLEICH")
print("=" * 65)

print(
    f"\nKlassischer optimaler Wert: {classical_value}"
)

print(
    f"QAOA-Wert:                  {qaoa_value}"
)


# Prüfen, ob QAOA das Optimum gefunden hat

if qaoa_value == classical_value:

    print(
        "\n✓ QAOA hat die optimale Lösung gefunden."
    )

else:

    print(
        "\n⚠ QAOA hat nicht die optimale Lösung gefunden."
    )


# ============================================================
# 16. QUALITÄT DER QAOA-LÖSUNG
# ============================================================

if classical_value > 0:

    quality = (
        qaoa_value /
        classical_value *
        100
    )

    print(
        f"\nLösungsqualität von QAOA: "
        f"{quality:.1f}%"
    )


# ============================================================
# 17. ROHDATEN AUSGEBEN
# ============================================================

print("\n")
print("=" * 65)
print("QISKIT-ERGEBNISSE")
print("=" * 65)

print("\nKlassische Lösung:")
print(classical_result.x)

print("\nQAOA Lösung:")
print(qaoa_result.x)