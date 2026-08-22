# ============================================================
# Travelling-Salesman-Problem (TSP) mit Qiskit
# ============================================================
#
# Problem:
# Ein Lieferfahrer startet bei A, muss B und C besuchen
# und anschließend wieder nach A zurückkehren.
#
# Gesucht wird die kürzeste mögliche Rundtour.
#
# Orte:
# A = Lager
# B = Kunde 1
# C = Kunde 2
#
# Entfernungen:
#
# A <-> B = 4 km
# A <-> C = 2 km
# B <-> C = 3 km
#
# Mögliche Rundtouren:
#
# A -> B -> C -> A
# = 4 + 3 + 2
# = 9 km
#
# A -> C -> B -> A
# = 2 + 3 + 4
# = 9 km
#
# Beide Lösungen sind hier gleich gut.
# ============================================================


from qiskit_optimization import QuadraticProgram
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler

from qiskit_optimization.converters import (
    LinearEqualityToPenalty
)


# ------------------------------------------------------------
# 1. Orte definieren
# ------------------------------------------------------------

orte = ["A", "B", "C"]


# ------------------------------------------------------------
# 2. Entfernungsmatrix
# ------------------------------------------------------------
#
# Die Zeilen und Spalten entsprechen den Orten:
#
#       A   B   C
# A     0   4   2
# B     4   0   3
# C     2   3   0
#
# distanz[i][j] = Entfernung von Ort i nach Ort j
#

distanz = [
    [0, 4, 2],
    [4, 0, 3],
    [2, 3, 0]
]


# ------------------------------------------------------------
# 3. Optimierungsproblem erstellen
# ------------------------------------------------------------

problem = QuadraticProgram()


# ------------------------------------------------------------
# 4. Binäre Variablen erzeugen
# ------------------------------------------------------------
#
# Wir müssen für jeden Ort und jede Position der Route
# eine Variable erzeugen.
#
# x_i_j bedeutet:
#
# x_i_j = 1
# -> Ort i befindet sich an Position j der Route
#
# x_i_j = 0
# -> Ort i befindet sich dort nicht.
#
# Bei 3 Orten gibt es also 3 x 3 = 9 Variablen.
#
# Beispiel:
#
# x_A_0 = 1
# -> A steht an Position 0
#

for i in range(3):
    for j in range(3):
        problem.binary_var(name=f"x_{i}_{j}")


# ------------------------------------------------------------
# 5. Zielfunktion aufbauen
# ------------------------------------------------------------
#
# Wir möchten die Gesamtstrecke minimieren.
#
# Wenn zwei aufeinanderfolgende Orte i und k gewählt werden,
# entstehen Kosten entsprechend der Entfernung.
#
# Beispiel:
#
# A -> B = 4 km
#
# Deshalb soll die Kombination
#
# x_A_0 * x_B_1
#
# mit 4 bestraft werden.
#
# Das Gleiche machen wir für alle möglichen Kombinationen.
#

quadratic = {}


for position in range(3):

    # Nächste Position.
    #
    # Nach der letzten Position geht es wieder
    # zurück zur ersten Position.
    next_position = (position + 1) % 3

    for i in range(3):
        for k in range(3):

            if i != k:

                variable1 = f"x_{i}_{position}"
                variable2 = f"x_{k}_{next_position}"

                quadratic[(variable1, variable2)] = distanz[i][k]


# ------------------------------------------------------------
# 6. Zielfunktion setzen
# ------------------------------------------------------------
#
# Wir wollen die Gesamtstrecke MINIMIEREN.
#

problem.minimize(
    quadratic=quadratic
)


# ------------------------------------------------------------
# 7. Nebenbedingungen
# ------------------------------------------------------------
#
# Jede Position der Route darf genau einen Ort enthalten.
#
# Beispiel:
#
# Position 0:
#
# x_A_0 + x_B_0 + x_C_0 = 1
#
# bedeutet:
# An Position 0 darf genau ein Ort stehen.
#

for position in range(3):

    linear = {}

    for i in range(3):
        linear[f"x_{i}_{position}"] = 1

    problem.linear_constraint(
        linear=linear,
        sense="==",
        rhs=1,
        name=f"Position_{position}"
    )


# ------------------------------------------------------------
# 8. Jeder Ort darf nur einmal vorkommen
# ------------------------------------------------------------
#
# Beispiel für A:
#
# x_A_0 + x_A_1 + x_A_2 = 1
#
# A darf also nur an genau einer Position stehen.
#

for i in range(3):

    linear = {}

    for position in range(3):
        linear[f"x_{i}_{position}"] = 1

    problem.linear_constraint(
        linear=linear,
        sense="==",
        rhs=1,
        name=f"Ort_{i}"
    )


# ------------------------------------------------------------
# 9. Problem anzeigen
# ------------------------------------------------------------

print("Optimierungsproblem:")
print(problem)


# ------------------------------------------------------------
# 10. QUBO erzeugen
# ------------------------------------------------------------
#
# QAOA benötigt eine Formulierung ohne klassische
# Gleichheits-Nebenbedingungen.
#
# Die Nebenbedingungen werden deshalb mit einem Strafterm
# in die Zielfunktion eingebaut.
#

converter = LinearEqualityToPenalty(
    penalty=20
)

qubo = converter.convert(problem)


# ------------------------------------------------------------
# 11. QAOA vorbereiten
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
# 12. QAOA ausführen
# ------------------------------------------------------------

result = qaoa.solve(qubo)


# ------------------------------------------------------------
# 13. Ergebnis ausgeben
# ------------------------------------------------------------

print("\nQAOA-Ergebnis:")
print(result)


# ------------------------------------------------------------
# 14. Route aus den Qubit-Ergebnissen rekonstruieren
# ------------------------------------------------------------

loesung = result.x

route = []

for position in range(3):

    for i in range(3):

        variable_name = f"x_{i}_{position}"

        # Position der Variable im Ergebnis bestimmen
        index = qubo.variables.index(variable_name)

        # Auf 0 oder 1 runden
        genommen = round(loesung[index])

        if genommen == 1:
            route.append(orte[i])


# ------------------------------------------------------------
# 15. Route anzeigen
# ------------------------------------------------------------

print("\nGefundene Route:")

print(" -> ".join(route) + " -> " + route[0])


# ------------------------------------------------------------
# 16. Gesamtdistanz berechnen
# ------------------------------------------------------------

gesamtstrecke = 0

for i in range(len(route)):

    aktueller_ort = orte.index(route[i])

    naechster_ort = orte.index(
        route[(i + 1) % len(route)]
    )

    gesamtstrecke += distanz[
        aktueller_ort
    ][
        naechster_ort
    ]


print("\nGesamtstrecke:", gesamtstrecke, "km")