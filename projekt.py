# ============================================================
# INVESTITIONSPROBLEM MIT 3 QUBITS
# ============================================================
#
# Ein Unternehmen möchte Projekte auswählen.
#
# Ziel:
#   Maximiere den Gewinn
#   unter Einhaltung des Budgets.
#
# ------------------------------------------------------------
# Projekte
#
# Projekt A:
#   Kosten  = 4 Mio. €
#   Gewinn  = 9
#
# Projekt B:
#   Kosten  = 3 Mio. €
#   Gewinn  = 7
#
# Projekt C:
#   Kosten  = 2 Mio. €
#   Gewinn  = 4
#
# Budget = 7 Mio. €
#
# ------------------------------------------------------------
#
# Qubit 0 -> Projekt A
# Qubit 1 -> Projekt B
# Qubit 2 -> Projekt C
#
# |000> -> kein Projekt
# |001> -> C
# |010> -> B
# |011> -> B + C
# |100> -> A
# |101> -> A + C
# |110> -> A + B
# |111> -> A + B + C
#
# ============================================================


import numpy as np

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from scipy.optimize import minimize


# ============================================================
# 1. PROBLEMDATEN
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

budget = 7


# ============================================================
# 2. PENALTY
# ============================================================
#
# Wenn eine Auswahl das Budget überschreitet,
# bekommt sie eine starke Strafe.
#
# Dadurch versucht QAOA automatisch,
# ungültige Lösungen zu vermeiden.
#
# ============================================================

penalty = 10


# ============================================================
# 3. Kostenfunktion
# ============================================================
#
# Für einen Bitstring berechnen wir:
#
#   Gewinn - Strafe
#
# Je größer dieser Wert ist,
# desto besser ist die Lösung.
#
# ============================================================

def score(bitstring):

    # Bitstring umdrehen, weil Qiskit bei der Ausgabe
    # die Qubit-Reihenfolge umkehrt.
    bits = bitstring[::-1]

    total_cost = 0
    total_profit = 0

    for i, project in enumerate(projects):

        if bits[i] == "1":

            total_cost += projects[project]["cost"]
            total_profit += projects[project]["profit"]

    # Überschreitung des Budgets bestrafen

    if total_cost > budget:

        excess = total_cost - budget

        total_profit -= penalty * excess

    return total_profit


# ============================================================
# 4. Alle möglichen Lösungen überprüfen
# ============================================================
#
# Das machen wir hier nur zur Kontrolle.
#
# Ein echtes Quantenprogramm würde diese vollständige
# Suche natürlich gerade vermeiden wollen.
#
# ============================================================

print("=" * 60)
print("INVESTITIONSPROBLEM")
print("=" * 60)

print("\nAlle möglichen Kombinationen:\n")

all_solutions = []

for number in range(8):

    bitstring = format(number, "03b")

    bits = bitstring[::-1]

    cost = 0
    profit = 0
    selected = []

    for i, project in enumerate(projects):

        if bits[i] == "1":

            selected.append(project)

            cost += projects[project]["cost"]
            profit += projects[project]["profit"]

    valid = cost <= budget

    if valid:

        all_solutions.append(
            (bitstring, selected, cost, profit)
        )

    print(
        f"{bitstring}  "
        f"{'+'.join(selected) if selected else '-':6}  "
        f"Kosten: {cost}  "
        f"Gewinn: {profit}  "
        f"{'✓' if valid else '✗'}"
    )


# ============================================================
# 5. Klassisch optimale Lösung
# ============================================================

classical_best = max(
    all_solutions,
    key=lambda x: x[3]
)

print("\nKlassisch optimale Lösung:")
print(
    classical_best[0],
    "->",
    " + ".join(classical_best[1]),
    "| Kosten:",
    classical_best[2],
    "| Gewinn:",
    classical_best[3]
)


# ============================================================
# 6. QAOA COST HAMILTONIAN
# ============================================================
#
# Wir bauen jetzt den Quantenschaltkreis direkt auf.
#
# Jedes Basiszustands |000> ... |111> bekommt eine
# entsprechende Bewertung.
#
# ============================================================

cost_values = []

for number in range(8):

    bitstring = format(number, "03b")

    cost_values.append(
        score(bitstring)
    )

cost_values = np.array(cost_values)


# ============================================================
# 7. QAOA-Schaltkreis
# ============================================================

def create_qaoa_circuit(gamma, beta):

    qc = QuantumCircuit(3)

    # --------------------------------------------------------
    # Superposition
    # --------------------------------------------------------
    #
    # Alle 8 möglichen Projektkombinationen werden erzeugt.
    #

    qc.h([0, 1, 2])


    # --------------------------------------------------------
    # Cost Layer
    # --------------------------------------------------------
    #
    # Jeder Zustand erhält eine Phasenänderung entsprechend
    # seiner Bewertung.
    #
    # Für ein kleines Beispiel können wir diesen Schritt
    # über einen diagonal definierten Operator darstellen.
    # --------------------------------------------------------

    phases = np.exp(
        1j * gamma * cost_values
    )

    qc.unitary(
        np.diag(phases),
        [0, 1, 2],
        label="Cost"
    )


    # --------------------------------------------------------
    # Mixer Layer
    # --------------------------------------------------------
    #
    # Der Mixer ermöglicht es, zwischen verschiedenen
    # möglichen Projektkombinationen zu wechseln.
    # --------------------------------------------------------

    for qubit in range(3):

        qc.rx(
            2 * beta,
            qubit
        )

    return qc


# ============================================================
# 8. QAOA-Ziel funktion
# ============================================================
#
# Wir simulieren den Quantenzustand und bestimmen den
# erwarteten Score.
#
# Der klassische Optimierer versucht anschließend,
# gamma und beta so einzustellen, dass der Score maximal wird.
#
# ============================================================

simulator = AerSimulator(
    method="statevector"
)


def objective(parameters):

    gamma, beta = parameters

    qc = create_qaoa_circuit(
        gamma,
        beta
    )

    qc.save_statevector()

    result = simulator.run(qc).result()

    statevector = result.get_statevector()

    probabilities = np.abs(
        statevector
    ) ** 2

    expectation = np.sum(
        probabilities * cost_values
    )

    # scipy minimiert.
    # Wir wollen aber maximieren.
    return -expectation


# ============================================================
# 9. QAOA Parameter optimieren
# ============================================================

optimization = minimize(
    objective,
    x0=[0.5, 0.5],
    method="COBYLA",
    options={
        "maxiter": 100
    }
)


gamma, beta = optimization.x


print("\nOptimierte QAOA-Parameter:")
print("gamma =", gamma)
print("beta  =", beta)


# ============================================================
# 10. Finalen Quantenschaltkreis erstellen
# ============================================================

qc = create_qaoa_circuit(
    gamma,
    beta
)

qc.measure_all()


print("\nQuantenschaltkreis:")
print(qc)


# ============================================================
# 11. Quantenmessung
# ============================================================

job = simulator.run(
    qc,
    shots=2000
)

result = job.result()

counts = result.get_counts()


# ============================================================
# 12. Wahrscheinlichkeiten anzeigen
# ============================================================

print("\nQAOA Messergebnisse:")
print()

for state, count in sorted(
    counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    percentage = (
        count / 2000 * 100
    )

    print(
        f"{state} : "
        f"{count:4d} "
        f"({percentage:5.1f} %)"
    )


# ============================================================
# 13. Beste gemessene Lösung bestimmen
# ============================================================

best_state = max(
    counts,
    key=counts.get
)


# Wegen Qiskits Bit-Reihenfolge
# wieder zurückdrehen.

display_state = best_state[::-1]


# ============================================================
# 14. Lösung auswerten
# ============================================================

selected = []

total_cost = 0
total_profit = 0

for i, project in enumerate(projects):

    if display_state[i] == "1":

        selected.append(project)

        total_cost += projects[project]["cost"]

        total_profit += projects[project]["profit"]


# ============================================================
# 15. Ergebnis
# ============================================================

print("\n" + "=" * 60)
print("QAOA ERGEBNIS")
print("=" * 60)

print(
    "\nBitstring:",
    display_state
)

print(
    "Projekte:",
    " + ".join(selected)
)

print(
    "Kosten:",
    total_cost,
    "Mio. €"
)

print(
    "Gewinn:",
    total_profit
)

print(
    "Budget:",
    budget,
    "Mio. €"
)


# ============================================================
# 16. Vergleich
# ============================================================

print("\n" + "=" * 60)
print("VERGLEICH")
print("=" * 60)

print(
    "\nKlassisches Optimum:",
    classical_best[3]
)

print(
    "QAOA-Ergebnis:",
    total_profit
)


if total_profit == classical_best[3]:

    print(
        "\n✓ QAOA hat die optimale Lösung gefunden."
    )

else:

    print(
        "\n⚠ QAOA hat nicht das Optimum gefunden."
    )