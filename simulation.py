"""
Monte Carlo Simulation - Schach Kandidatenturnier 2026
======================================================
Wir lernen Monte Carlo Schritt für Schritt.

STUFE 1: Ein einzelnes Spiel simulieren
STUFE 2: Das ganze Turnier simulieren (Round-Robin)
"""

import random

# ============================================================
# SCHRITT 1: Die Spieler definieren
# ============================================================
# Jeder Spieler ist ein Dictionary mit Name und Elo-Zahl.
# Die Elo-Zahl ist unser wichtigster Input - sie sagt aus,
# wie stark ein Spieler ist.

SPIELER = [
    {"name": "Caruana",        "elo": 2795},
    {"name": "Nakamura",       "elo": 2810},
    {"name": "Praggnanandhaa", "elo": 2758},
    {"name": "Giri",           "elo": 2760},
    {"name": "Wei Yi",         "elo": 2754},
    {"name": "Sindarov",       "elo": 2726},
    {"name": "Esipenko",       "elo": 2698},
    {"name": "Blübaum",        "elo": 2679},
]


# ============================================================
# SCHRITT 2: Die Elo-Formel
# ============================================================
# Formel: P(A gewinnt) = 1 / (1 + 10^((Elo_B - Elo_A) / 400))
#
# Warum 400? Das ist eine historisch kalibrierte Konstante.
# Bei Elo-Differenz 400 gewinnt der Stärkere ~91% der Partien.
# Bei Elo-Differenz 0 gewinnt jeder 50%.

def elo_gewinnwahrscheinlichkeit(elo_a, elo_b):
    """Gibt die Wahrscheinlichkeit zurück, dass Spieler A gewinnt."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


# ============================================================
# SCHRITT 3: Remis einbauen - das Schach-Problem
# ============================================================
# Elo gibt uns nur P(A gewinnt) vs P(B gewinnt).
# Aber im Schach gibt es 3 Ergebnisse: Sieg, Remis, Niederlage.
#
# Modell:
#   1. Remisrate hängt von der Elo-Differenz ab
#   2. Den restlichen "Entscheidungs-Pool" verteilen wir per Elo-Formel

def partie_wahrscheinlichkeiten(elo_a, elo_b):
    """
    Gibt (p_sieg_a, p_remis, p_sieg_b) zurück.
    Die drei Werte summieren sich immer zu 1.0
    """
    elo_differenz = abs(elo_a - elo_b)
    remisrate = max(0.40, 0.58 - elo_differenz * 0.001)

    entscheidungspool = 1 - remisrate
    p_a_gewinnt_wenn_entscheidung = elo_gewinnwahrscheinlichkeit(elo_a, elo_b)

    p_sieg_a = entscheidungspool * p_a_gewinnt_wenn_entscheidung
    p_sieg_b = entscheidungspool * (1 - p_a_gewinnt_wenn_entscheidung)

    return p_sieg_a, remisrate, p_sieg_b


# ============================================================
# SCHRITT 4: Eine Partie simulieren - der Monte Carlo Kern!
# ============================================================
# Wir ziehen eine Zufallszahl und schauen in welches
# "Wahrscheinlichkeits-Segment" sie fällt:
#
#  0.0      0.35         0.81       1.0
#   |--A gewinnt--|--Remis--|--B gewinnt--|

def partie_spielen(spieler_a, spieler_b):
    """
    Simuliert eine Partie. Gibt zurück:
    - (1.0, 0.0) wenn A gewinnt  → A bekommt 1 Punkt
    - (0.5, 0.5) bei Remis       → beide bekommen 0.5
    - (0.0, 1.0) wenn B gewinnt  → B bekommt 1 Punkt
    """
    p_a, p_remis, p_b = partie_wahrscheinlichkeiten(
        spieler_a["elo"], spieler_b["elo"]
    )

    zufallszahl = random.random()

    if zufallszahl < p_a:
        return 1.0, 0.0
    elif zufallszahl < p_a + p_remis:
        return 0.5, 0.5
    else:
        return 0.0, 1.0


# ============================================================
# STUFE 2: DAS GANZE TURNIER SIMULIEREN
# ============================================================
# Format: Round-Robin, doppelte Runde
# = jeder spielt gegen jeden ZWEIMAL (einmal Weiß, einmal Schwarz)
# = 8 Spieler × 7 Gegner × 2 = 14 Partien pro Spieler = 56 Partien gesamt

def turnier_spielen(spieler_liste):
    """
    Simuliert ein komplettes Round-Robin Turnier.
    Gibt { "Caruana": 8.5, "Nakamura": 9.0, ... } zurück.
    """
    punkte = {s["name"]: 0.0 for s in spieler_liste}
    n = len(spieler_liste)

    for i in range(n):
        for j in range(i + 1, n):
            a, b = spieler_liste[i], spieler_liste[j]

            # Partie 1: A hat Weiß
            p_a, p_b = partie_spielen(a, b)
            punkte[a["name"]] += p_a
            punkte[b["name"]] += p_b

            # Partie 2: B hat Weiß
            p_b, p_a = partie_spielen(b, a)
            punkte[a["name"]] += p_a
            punkte[b["name"]] += p_b

    return punkte


def turnier_rangliste(punkte):
    """Sortiert die Spieler nach Punkten, gibt geordnete Liste zurück."""
    return sorted(punkte.items(), key=lambda x: x[1], reverse=True)


# ============================================================
# STUFE 3: MONTE CARLO - 100.000 TURNIERE SIMULIEREN
# ============================================================
# Idee:
#   Wir simulieren das Turnier N-mal.
#   Jedes Mal zählen wir: Wer hat gewonnen?
#   Am Ende: gewinn_chance = siege / N
#
# Gesetz der großen Zahlen:
#   N=1.000   → grobe Schätzung (±2%)
#   N=10.000  → stabil          (±0.5%)
#   N=100.000 → sehr präzise    (±0.2%)

def monte_carlo(spieler_liste, n_simulationen=100_000):
    """
    Simuliert das Turnier n_simulationen-mal.
    Gibt Sieg-%, Top3-% und Ø-Punkte pro Spieler zurück.
    """
    ergebnisse = {
        s["name"]: {"siege": 0, "top3": 0, "punkte_gesamt": 0.0}
        for s in spieler_liste
    }

    for _ in range(n_simulationen):
        punkte = turnier_spielen(spieler_liste)
        rangliste = turnier_rangliste(punkte)

        ergebnisse[rangliste[0][0]]["siege"] += 1

        for platz, (name, pts) in enumerate(rangliste, 1):
            if platz <= 3:
                ergebnisse[name]["top3"] += 1
            ergebnisse[name]["punkte_gesamt"] += pts

    for name in ergebnisse:
        ergebnisse[name]["sieg_chance"] = ergebnisse[name]["siege"] / n_simulationen
        ergebnisse[name]["top3_chance"] = ergebnisse[name]["top3"] / n_simulationen
        ergebnisse[name]["avg_punkte"]  = ergebnisse[name]["punkte_gesamt"] / n_simulationen

    return ergebnisse


# ============================================================
# AUSGABE & STUFE 4: VISUALISIERUNG
# ============================================================

if __name__ == "__main__":
    N = 100_000
    print(f"\nMonte Carlo mit {N:,} Simulationen läuft...\n")

    ergebnisse = monte_carlo(SPIELER, n_simulationen=N)

    ranking = sorted(ergebnisse.items(), key=lambda x: x[1]["sieg_chance"], reverse=True)

    print(f"  {'Spieler':<20} {'Elo':<6} {'Sieg-%':>7}  {'Top3-%':>7}  {'Ø Punkte':>9}")
    print(f"  {'-'*55}")
    for name, stats in ranking:
        elo = next(s["elo"] for s in SPIELER if s["name"] == name)
        print(
            f"  {name:<20} {elo:<6} "
            f"{stats['sieg_chance']:>7.1%}  "
            f"{stats['top3_chance']:>7.1%}  "
            f"{stats['avg_punkte']:>9.2f}"
        )
    print(f"\n  Summe: {sum(s['sieg_chance'] for _,s in ranking):.1%}  (muss 100% sein)")

    # Visualisierung
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    namen = [name for name, _ in ranking]
    siege = [stats["sieg_chance"] * 100 for _, stats in ranking]
    top3  = [stats["top3_chance"] * 100 for _, stats in ranking]
    elos  = [next(s["elo"] for s in SPIELER if s["name"] == name) for name in namen]

    farben_sieg = ["#1a3a6b" if e >= 2780 else "#2e6db4" if e >= 2740 else "#7bafd4" for e in elos]
    farben_top3 = ["#8b1a1a" if e >= 2780 else "#c0392b" if e >= 2740 else "#e08080" for e in elos]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"Schach Kandidatenturnier 2026\nMonte Carlo Simulation ({N:,} Turniere)",
        fontsize=14, fontweight="bold", y=1.01
    )

    for ax, werte, farben, titel in [
        (ax1, siege, farben_sieg, "Turniersieg"),
        (ax2, top3,  farben_top3, "Top-3 Platzierung"),
    ]:
        balken = ax.barh(namen[::-1], werte[::-1], color=farben[::-1], edgecolor="white", height=0.6)
        ax.set_xlabel("Wahrscheinlichkeit (%)", fontsize=11)
        ax.set_title(titel, fontsize=12, fontweight="bold")
        ax.set_xlim(0, max(werte) * 1.25)
        for bar, wert in zip(balken, werte[::-1]):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{wert:.1f}%", va="center", fontsize=10)
        labels = [f"{n}  ({e})" for n, e in zip(namen[::-1], elos[::-1])]
        ax.set_yticks(range(len(namen)))
        ax.set_yticklabels(labels, fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("kandidatenturnier_2026.png", dpi=150, bbox_inches="tight")
    print(f"\n  → Grafik gespeichert als: kandidatenturnier_2026.png")
