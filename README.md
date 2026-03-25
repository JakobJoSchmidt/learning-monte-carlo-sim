# Chess Candidates Tournament 2026 — Monte Carlo Simulation 

> A step-by-step Monte Carlo simulation to predict win probabilities for the 2026 Chess Candidates Tournament. Built as a learning project.

-----

## What is Monte Carlo Simulation?

Instead of deriving a closed-form formula, we simulate the entire tournament thousands of times and count how often each player wins. The **Law of Large Numbers** then gives us stable probabilities.

```python
win_probability("Nakamura") = wins_in_simulation / total_simulations
```

The more simulations you run, the more precise the result:

  * **N = 1,000** → rough estimate (±2%)
  * **N = 10,000** → reliable (±0.5%)
  * **N = 100,000** → very stable (±0.2%)

-----

## Tournament Format

The tournament is played in a **Double Round-Robin** format, meaning each player plays every other player twice (once as White, once as Black).

  * **14 games per player** (8 players × 7 opponents × 2)
  * **56 games total** in the tournament
  * **Scoring:** Win = 1 pt, Draw = 0.5 pt, Loss = 0 pt

-----

## Players (2026 Field)

| Player | Elo | Qualification Path |
| :--- | :--- | :--- |
| **Hikaru Nakamura** | 2810 | World Rankings |
| **Fabiano Caruana** | 2795 | FIDE Circuit 2024 winner |
| **Anish Giri** | 2760 | Grand Swiss 2025 winner |
| **Praggnanandhaa** | 2758 | FIDE Circuit 2025 winner |
| **Wei Yi** | 2754 | World Cup 2025 runner-up |
| **Sindarov** | 2726 | World Cup 2025 winner |
| **Esipenko** | 2698 | World Cup 2025 third place |
| **Blübaum** | 2679 | Grand Swiss 2025 runner-up |

-----

## How the Model Works

### Step 1 — Elo Win Probability

The Elo formula gives the probability that player A beats player B in a decisive game:

$$P(A) = \frac{1}{1 + 10^{(E_B - E_A) / 400}}$$

  * **Elo difference 0:** both players win 50% of decisive games.
  * **Elo difference 400:** the stronger player wins \~91% of decisive games.

### Step 2 — Modeling Draws

At the top level, \~55–58% of games are drawn. The Elo formula alone doesn't account for this, so we use a simple draw model:

```python
draw_rate = max(0.40, 0.58 - elo_difference * 0.001)
```

The remaining probability is split between a win and a loss via the Elo formula. This gives three outcomes per game (Win, Draw, Loss) which sum to exactly 100%.

### Step 3 — Simulate One Game

We draw a random number between `0.0` and `1.0` and check which probability segment it falls into:

```text
0.0       0.35      0.81      1.0
 |---A wins---|---Draw---|---B wins---|

random = 0.15 → A wins
random = 0.50 → Draw
random = 0.90 → B wins
```

### Step 4 — Simulate the Full Tournament

We loop through all 28 pairings, play each twice (colors swapped), and accumulate the points.

### Step 5 — Monte Carlo (100,000 runs)

We repeat the full tournament 100,000 times and count the outcomes. The final result is the simulated win probability for each player.

-----

## Results

*After 100,000 simulations:*

| Player | Elo | Win % | Top-3 % | Avg Points |
| :--- | :--- | :--- | :--- | :--- |
| **Nakamura** | 2810 | 27.1% | 62.3% | 7.71 |
| **Caruana** | 2795 | 25.1% | 59.1% | 7.53 |
| **Praggnanandhaa** | 2758 | 12.4% | 42.1% | 7.12 |
| **Giri** | 2760 | 11.8% | 40.8% | 7.15 |
| **Wei Yi** | 2754 | 10.1% | 36.4% | 7.08 |
| **Sindarov** | 2726 | 6.3% | 26.3% | 6.76 |
| **Esipenko** | 2698 | 4.1% | 18.7% | 6.44 |
| **Blübaum** | 2679 | 3.1% | 14.3% | 6.21 |

-----

## Model Limitations

This is a simplified baseline model that uses only the standard Elo rating as input. The following variables would increase its accuracy:

  * **Play style variance:** The model does not account for individual playing styles. A safe, solid style typically leads to lower variance (fewer extreme high and low scores), whereas a high-risk, dynamic style increases fluctuations in both directions. Or in other words: Some players draw far more frequently than others.
  * **Recent form:** Weighting the last x games more heavily than historical data.
  * **Head-to-head history:** Some players consistently outperform their standard Elo against specific opponents.
  * **Color-specific performance:** The White piece advantage varies significantly by player.

-----

## Requirements & Usage

First, install the required dependencies:

```bash
pip install matplotlib
```

Then, run the simulation script:

```bash
python simulation.py
```

> **Note:** This runs 100,000 tournament simulations (which takes \~4 seconds) and automatically saves the resulting chart as `kandidatenturnier_2026.png`.

