# ============================================================
# RUCKSACKPROBLEM – optimierte Qiskit-Version
# ============================================================
#
# Ziel:
#   Maximiere den Wert der Gegenstände,
#   ohne die maximale Traglast zu überschreiten.
#
# Rucksackkapazität: 7 kg
#
# Gegenstände:
#   Laptop  -> 4 kg, Wert 7
#   Kamera  -> 3 kg, Wert 6
#   Buch    -> 2 kg, Wert 4
#   Wasser  -> 1 kg, Wert 2
#
# ============================================================

from qiskit_optimization import QuadraticProgram
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler
from qiskit_optimization.converters import (
    LinearInequalityToPenalty
)


# ------------------------------------------------------------
# 1. Daten
# ------------------------------------------------------------

items = {
    "Laptop": {"weight": 4, "value": 7},
    "Kamera": {"weight": 3, "value": 6},
    "Buch":   {"weight": 2, "value": 4},
    "Wasser": {"weight": 1, "value": 2},
}

capacity = 7


# ------------------------------------------------------------
# 2. Optimierungsproblem erstellen
# ------------------------------------------------------------

problem = QuadraticProgram(
    name="Rucksackproblem"
)


# Für jeden Gegenstand wird eine Binärvariable erzeugt.
#
# x = 1 -> Gegenstand wird genommen
# x = 0 -> Gegenstand wird nicht genommen

for item in items:
    problem.binary_var(name=item)


# ------------------------------------------------------------
# 3. Zielfunktion
# ------------------------------------------------------------
#
# Wir wollen den Gesamtwert MAXIMIEREN.
#
# Qiskit erzeugt daraus:
#
# 7 * Laptop
# + 6 * Kamera
# + 4 * Buch
# + 2 * Wasser
#
# ------------------------------------------------------------

problem.maximize(
    linear={
        item: data["value"]
        for item, data in items.items()
    }
)


# ------------------------------------------------------------
# 4. Gewichtsbeschränkung
# ------------------------------------------------------------
#
# Das Gesamtgewicht darf höchstens 7 kg betragen:
#
# 4*Laptop
# + 3*Kamera
# + 2*Buch
# + 1*Wasser <= 7
#
# ------------------------------------------------------------

problem.linear_constraint(
    linear={
        item: data["weight"]
        for item, data in items.items()
    },
    sense="<=",
    rhs=capacity,
    name="Maximales_Gewicht"
)


# ------------------------------------------------------------
# 5. Problem anzeigen
# ------------------------------------------------------------

print("=" * 55)
print("RUCKSACKPROBLEM")
print("=" * 55)

print(problem)


# ------------------------------------------------------------
# 6. In QUBO umwandeln
# ------------------------------------------------------------
#
# QAOA arbeitet mit einer Zielfunktion ohne klassische
# Ungleichungsbedingungen.
#
# Die Gewichtsbeschränkung wird deshalb über einen
# Strafterm berücksichtigt.
#
# Je größer der Strafwert, desto stärker wird eine
# Überschreitung der Kapazität bestraft.
#
# ------------------------------------------------------------

converter = LinearInequalityToPenalty(
    penalty=20
)

qubo = converter.convert(problem)


# ------------------------------------------------------------
# 7. QAOA konfigurieren
# ------------------------------------------------------------

optimizer = COBYLA(
    maxiter=100
)

qaoa = QAOA(
    sampler=StatevectorSampler(),
    optimizer=optimizer,
    reps=2
)


# ------------------------------------------------------------
# 8. Optimierung durchführen
# ------------------------------------------------------------

result = qaoa.solve(qubo)


# ------------------------------------------------------------
# 9. Ergebnis auswerten
# ------------------------------------------------------------

print("\n" + "=" * 55)
print("ERGEBNIS")
print("=" * 55)

selected_items = []

total_weight = 0
total_value = 0


for item in items:

    # Wert der Variablen aus dem QAOA-Ergebnis
    selected = round(
        result.x[
            qubo.variables.index(item)
        ]
    )

    if selected == 1:

        selected_items.append(item)

        total_weight += items[item]["weight"]
        total_value += items[item]["value"]


# ------------------------------------------------------------
# 10. Ausgewählte Gegenstände anzeigen
# ------------------------------------------------------------

print("\nAusgewählte Gegenstände:")

for item in selected_items:

    print(
        f"  ✓ {item:<10}"
        f" Gewicht: {items[item]['weight']} kg"
        f" | Wert: {items[item]['value']}"
    )


# ------------------------------------------------------------
# 11. Zusammenfassung
# ------------------------------------------------------------

print("\n" + "-" * 55)

print(f"Gesamtgewicht : {total_weight} kg")
print(f"Gesamtwert    : {total_value}")
print(f"Kapazität     : {capacity} kg")

print("-" * 55)


if total_weight <= capacity:
    print("✓ Lösung erfüllt die Gewichtsbeschränkung.")
else:
    print("✗ Gewichtsbeschränkung wurde verletzt.")


print("\nQAOA hat folgende Lösung gefunden:")
print(result.x)