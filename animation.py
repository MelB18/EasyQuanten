import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import circuit_drawer


# ============================================================
# 1. Quantum Circuit definieren
# ============================================================

qc = QuantumCircuit(1)

qc.h(0)
qc.x(0)
qc.z(0)
qc.y(0)
qc.h(0)


# ============================================================
# 2. Zustände nach jedem Gate berechnen
# ============================================================

state = Statevector.from_label("0")

states = [state]
gate_names = ["Start"]

for instruction in qc.data:
    gate = instruction.operation

    state = state.evolve(gate)

    states.append(state)
    gate_names.append(gate.name.upper())


# ============================================================
# 3. Bloch-Vektor aus Statevector berechnen
# ============================================================

def bloch_vector(state):
    """
    Berechnet x, y, z des Bloch-Vektors.

    Für |psi> = alpha|0> + beta|1> gilt:

        x = 2 Re(alpha* beta)
        y = 2 Im(alpha* beta)
        z = |alpha|² - |beta|²
    """

    alpha = state.data[0]
    beta = state.data[1]

    x = 2 * np.real(np.conj(alpha) * beta)
    y = 2 * np.imag(np.conj(alpha) * beta)
    z = abs(alpha)**2 - abs(beta)**2

    return np.array([x, y, z])


# ============================================================
# 4. Matplotlib-Fenster
# ============================================================

fig = plt.figure(figsize=(12, 6))

# ------------------------------------------------------------
# Linke Seite: Quantum Circuit
# ------------------------------------------------------------

ax_circuit = fig.add_axes([0.05, 0.35, 0.4, 0.3])
ax_circuit.axis("off")

# Circuit als Matplotlib-Bild erzeugen
circuit_image = qc.draw(
    output="mpl",
    style="iqp"
)

# Wir speichern das Bild temporär
circuit_image.savefig("circuit.png", bbox_inches="tight")
plt.close(circuit_image)

circuit_img = plt.imread("circuit.png")

ax_circuit.imshow(circuit_img)
ax_circuit.axis("off")


# ------------------------------------------------------------
# Rechte Seite: Bloch-Kugel
# ------------------------------------------------------------

ax = fig.add_subplot(
    111,
    projection="3d",
    position=[0.55, 0.1, 0.4, 0.8]
)


# ============================================================
# 5. Bloch-Kugel zeichnen
# ============================================================

def draw_bloch_sphere(ax):

    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 30)

    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))

    ax.plot_wireframe(
        x, y, z,
        alpha=0.15,
        linewidth=0.5
    )

    # X-Achse
    ax.plot([-1, 1], [0, 0], [0, 0], alpha=0.4)

    # Y-Achse
    ax.plot([0, 0], [-1, 1], [0, 0], alpha=0.4)

    # Z-Achse
    ax.plot([0, 0], [0, 0], [-1, 1], alpha=0.4)

    # Beschriftungen
    ax.text(1.1, 0, 0, "|+⟩")
    ax.text(-1.2, 0, 0, "|-⟩")

    ax.text(0, 1.1, 0, "|+i⟩")
    ax.text(0, -1.2, 0, "|-i⟩")

    ax.text(0, 0, 1.15, "|0⟩")
    ax.text(0, 0, -1.2, "|1⟩")

    ax.set_xlim([-1.2, 1.2])
    ax.set_ylim([-1.2, 1.2])
    ax.set_zlim([-1.2, 1.2])

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")


# ============================================================
# 6. Animation
# ============================================================

def update(frame):

    ax.clear()

    draw_bloch_sphere(ax)

    vector = bloch_vector(states[frame])

    x, y, z = vector

    # Bloch-Vektor
    ax.quiver(
        0, 0, 0,
        x, y, z,
        linewidth=3,
        arrow_length_ratio=0.12
    )

    # Titel
    ax.set_title(
        f"Gate: {gate_names[frame]}",
        fontsize=16
    )

    # Statevector anzeigen
    state = states[frame]

    alpha = state.data[0]
    beta = state.data[1]

    fig.suptitle(
        f"Quantum State Visualization\n"
        f"|ψ⟩ = ({alpha:.2f})|0⟩ + ({beta:.2f})|1⟩",
        fontsize=14
    )


# ============================================================
# 7. Animation starten
# ============================================================

animation = FuncAnimation(
    fig,
    update,
    frames=len(states),
    interval=1500,       # 1.5 Sekunden pro Gate
    repeat=True
)

plt.show()