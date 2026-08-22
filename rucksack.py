# ============================================================
# Rucksackproblem mit Qiskit und QAOA
# ============================================================
#
# Ziel:
# Wir haben einen Rucksack mit maximal 7 kg.
# Wir wollen Gegenstände auswählen, sodass der Gesamtwert
# möglichst groß wird, ohne die Gewichtskapazität zu überschreiten.
#
# Gegenstände:
# 0: Laptop  -> 4 kg, Wert 7
# 1: Kamera  -> 3 kg, Wert 6
# 2: Buch    -> 2 kg, Wert 4
# 3: Wasser  -> 1 kg, Wert 2
#
# Eine Variable x_i bedeutet:
# x_i = 0 -> Gegenstand wird nicht genommen
# x_i = 1 -> Gegenstand wird genommen
#
# ============================================================


# Wir benötigen Qiskit und die Qiskit-Optimierungspakete
from qiskit_optimization import QuadraticProgram
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler

# Konverter von Optimierungsproblemen in Ising-Probleme
from qiskit_optimization.converters import LinearEqualityToPenalty

# ------------------------------------------------------------
# 1. Daten des Rucksackproblems
# ------------------------------------------------------------

gegenstaende = ["Laptop", "Kamera", "Buch", "Wasser"]

gewicht = [4, 3, 2, 1]
wert = [7, 6, 4, 2]

kapazitaet = 7


# ------------------------------------------------------------
# 2. Optimierungsproblem erstellen
# ------------------------------------------------------------

problem = QuadraticProgram()

# Für jeden Gegenstand erzeugen wir eine binäre Variable.
#
# Beispiel:
# x0 = 1 bedeutet: Laptop nehmen
# x0 = 0 bedeutet: Laptop nicht nehmen

for i in range(len(gegenstaende)):
    problem.binary_var(name=f"x{i}")


# ------------------------------------------------------------
# 3. Zielfunktion
# ------------------------------------------------------------
#
# Wir wollen den Gesamtwert MAXIMIEREN.
#
# Wert =
# 7*x0 + 6*x1 + 4*x2 + 2*x3
#
# Da die Optimierung später als Minimierungsproblem behandelt
# werden kann, kümmert sich Qiskit um die entsprechende
# Umformung.
#

problem.maximize(
    linear={
        "x0": wert[0],
        "x1": wert[1],
        "x2": wert[2],
        "x3": wert[3]
    }
)


# ------------------------------------------------------------
# 4. Gewichtsbedingung
# ------------------------------------------------------------
#
# Der Rucksack darf höchstens 7 kg wiegen.
#
# 4*x0 + 3*x1 + 2*x2 + 1*x3 <= 7
#

problem.linear_constraint(
    linear={
        "x0": gewicht[0],
        "x1": gewicht[1],
        "x2": gewicht[2],
        "x3": gewicht[3]
    },
    sense="<=",
    rhs=kapazitaet,
    name="Gewicht"
)


# ------------------------------------------------------------
# 5. Problem anzeigen
# ------------------------------------------------------------

print("Optimierungsproblem:")
print(problem)


# ------------------------------------------------------------
# 6. QUBO-Umwandlung
# ------------------------------------------------------------
#
# QAOA arbeitet mit einem Hamiltonoperator/Ising-Modell.
# Deshalb müssen wir unser Optimierungsproblem zunächst
# entsprechend umwandeln.
#
# Die Nebenbedingung
#
#     Gewicht <= 7
#
# wird dabei durch eine Strafterm-Methode berücksichtigt.
#

converter = LinearEqualityToPenalty(penalty=10)

qubo = converter.convert(problem)


# ------------------------------------------------------------
# 7. QAOA vorbereiten
# ------------------------------------------------------------
#
# QAOA = Quantum Approximate Optimization Algorithm
#
# Der Algorithmus versucht, einen möglichst guten Zustand
# für unser Optimierungsproblem zu finden.
#
# COBYLA ist ein klassischer Optimierer, der von QAOA verwendet
# wird, um die Parameter des Quantenkreises zu optimieren.
#

optimizer = COBYLA(maxiter=100)

qaoa = QAOA(
    sampler=StatevectorSampler(),
    optimizer=optimizer,
    reps=2
)


# ------------------------------------------------------------
# 8. QAOA ausführen
# ------------------------------------------------------------

result = qaoa.solve(qubo)


# ------------------------------------------------------------
# 9. Ergebnis auswerten
# ------------------------------------------------------------

print("\nErgebnis:")
print(result)


# Die binären Variablen aus dem Ergebnis auslesen.
#
# Beispiel:
# [1, 1, 0, 0]
#
# bedeutet:
# Laptop = 1
# Kamera = 1
# Buch   = 0
# Wasser = 0

loesung = result.x


# ------------------------------------------------------------
# 10. Ausgewählte Gegenstände anzeigen
# ------------------------------------------------------------

gesamtgewicht = 0
gesamtwert = 0

print("\nAusgewählte Gegenstände:")

for i in range(len(gegenstaende)):

    # Wegen möglicher kleiner numerischer Abweichungen
    # runden wir die Lösung auf 0 oder 1.
    genommen = round(loesung[i])

    if genommen == 1:

        print(
            f"- {gegenstaende[i]} "
            f"({gewicht[i]} kg, Wert {wert[i]})"
        )

        gesamtgewicht += gewicht[i]
        gesamtwert += wert[i]


# ------------------------------------------------------------
# 11. Zusammenfassung
# ------------------------------------------------------------

print("\n----------------------------")
print("Gesamtgewicht:", gesamtgewicht, "kg")
print("Gesamtwert:", gesamtwert)
print("----------------------------")

if gesamtgewicht <= kapazitaet:
    print("Die Gewichtskapazität wurde eingehalten.")
else:
    print("Die Gewichtskapazität wurde überschritten!")