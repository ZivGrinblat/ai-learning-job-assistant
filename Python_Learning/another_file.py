"""
Stats & Probability — Morning lesson (NumPy, Pandas, Matplotlib)

How to use this file tomorrow:
  1. Install once:  pip install numpy pandas matplotlib
  2. Run whole file:  python Python_Learning/another_file.py
  3. Or run one section at a time in the Python REPL — copy a section block.

Order of sections (each builds on the last):
  1. Randomness      — simulate a dice; probability by counting
  2. NumPy arrays    — mean, dot product, weighted average
  3. Pandas          — tabular data, errors, squared errors
  4. Probability     — simple rules with numbers
  5. Matplotlib      — plot a line y = mx + b

Key idea for the whole morning:
  Statistics = describe data (mean, spread, tables)
  Probability = how likely outcomes are (often estimated by simulation)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# SECTION 1 — Randomness: simulate a dice roll
# =============================================================================
# Probability of rolling a 6 on a fair die = 1/6.
# Instead of formulas first, we ROLL many times and COUNT.


def section_1_dice():
    print("\n" + "=" * 60)
    print("SECTION 1 — Randomness (dice simulation)")
    print("=" * 60)

    rng = np.random.default_rng(seed=42)  # seed = same "random" results every run

    one_roll = rng.integers(1, 7)  # 1..6 inclusive on upper bound in integers API
    print(f"One roll: {one_roll}")

    few_rolls = rng.integers(1, 7, size=10)
    many_rolls = rng.integers(1, 7, size=10_000)
    print(f"10 rolls:  {few_rolls}")
    print(f"First 20 of 10,000 rolls: {many_rolls[:20]} ...")

    # Estimate P(6) = (number of sixes) / (total rolls)
    sixes = np.sum(many_rolls == 6)
    estimated_p_six = sixes / len(many_rolls)
    print(f"Sixes in 10,000 rolls: {sixes}")
    print(f"Estimated P(6) ≈ {estimated_p_six:.4f}  (theory says 0.1667)")


# =============================================================================
# SECTION 2 — NumPy: arrays, mean, dot product
# =============================================================================
# np.array  = list of numbers you can compute on in one shot
# np.mean   = average
# np.dot(a, b) = a1*b1 + a2*b2 + ...  (also: weighted sum if b are weights)


def section_2_numpy_basics():
    print("\n" + "=" * 60)
    print("SECTION 2 — NumPy arrays, mean, dot product")
    print("=" * 60)

    # --- Shopping bill (your original quantities × costs idea) ---
    quantities = np.array([2, 12, 3])
    costs = np.array([12.5, 0.5, 1.75])

    # Loop version (clear logic)
    partial_costs = []
    for quantity, cost in zip(quantities, costs):
        partial_costs.append(quantity * cost)
    total_loop = sum(partial_costs)

    # NumPy version (same math, one line)
    total_dot = np.dot(quantities, costs)

    print("Item breakdown:")
    for q, c in zip(quantities, costs):
        print(f"  {q:2d} × {c:5.2f} = {q * c:6.2f}")
    print(f"Total (loop): {total_loop:.2f}")
    print(f"Total (dot):  {total_dot:.2f}")

    # --- Mean = special case of weighted average with equal weights ---
    values = np.array([10.0, 20.0, 30.0])
    weights = np.array([1 / 3, 1 / 3, 1 / 3])  # each value counts equally

    mean_via_np = np.mean(values)
    mean_via_dot = np.dot(weights, values)

    print(f"\nValues: {values}")
    print(f"Mean via np.mean:     {mean_via_np}")
    print(f"Mean via dot(weights): {mean_via_dot}")

    # --- Sum of squares (used later in stats for variance / errors) ---
    errors = np.array([5, -5, 3.2, -1.1])
    sum_of_squares = np.dot(errors, errors)  # 5² + (-5)² + 3.2² + (-1.1)²
    print(f"\nErrors: {errors}")
    print(f"Sum of squared errors (dot): {sum_of_squares:.2f}")
    print(f"Same via (errors**2).sum(): {(errors ** 2).sum():.2f}")


# =============================================================================
# SECTION 3 — Pandas: tables for data
# =============================================================================
# DataFrame = spreadsheet in Python (columns, rows, labels)


def section_3_pandas_table():
    print("\n" + "=" * 60)
    print("SECTION 3 — Pandas DataFrame")
    print("=" * 60)

    errors = np.array([5.0, -5.0, 3.2, -1.1])

    df = pd.DataFrame(
        {
            "error": errors,
            "squared_error": errors ** 2,  # element-wise square, NOT np.dot scalar
        }
    )

    print(df)
    print(f"\nMean error:          {df['error'].mean():.2f}")
    print(f"Mean squared error:  {df['squared_error'].mean():.2f}")

    # Dice rolls as a table
    rng = np.random.default_rng(0)
    rolls = rng.integers(1, 7, size=20)
    dice_df = pd.DataFrame({"roll": rolls})
    print("\n20 dice rolls as a table:")
    print(dice_df)
    print("\nValue counts (how often each face appeared):")
    print(dice_df["roll"].value_counts().sort_index())


# =============================================================================
# SECTION 4 — Probability rules (pen and paper, then code)
# =============================================================================
# P(A) = favorable / total   (if all outcomes equally likely)
# P(A or B) for mutually exclusive events = P(A) + P(B)


def section_4_probability_rules():
    print("\n" + "=" * 60)
    print("SECTION 4 — Basic probability rules")
    print("=" * 60)

    # Fair die: P(even) = P(2) + P(4) + P(6) = 3/6
    p_even = 3 / 6
    p_greater_than_4 = 2 / 6  # only 5 and 6
    print(f"P(even on die)     = 3/6 = {p_even:.3f}")
    print(f"P(roll > 4)        = 2/6 = {p_greater_than_4:.3f}")

    # Check simulation matches theory (Section 1 idea)
    rng = np.random.default_rng(1)
    rolls = rng.integers(1, 7, size=100_000)
    sim_p_even = np.mean(rolls % 2 == 0)  # True=1, False=0 → average = proportion
    print(f"Simulated P(even)  = {sim_p_even:.4f}")


# =============================================================================
# SECTION 5 — Matplotlib: visualize y = mx + b
# =============================================================================
# Your original "paint by numbers" idea — plot a straight line.
# xs = x values, ys = y values, ax.plot connects the dots.


def high_school_style(ax: plt.Axes) -> None:
    """Simple axes like a school graph: grid, centered axes through origin."""
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


def section_5_line_plot(save_path: str | None = None) -> None:
    print("\n" + "=" * 60)
    print("SECTION 5 — Matplotlib line plot (y = mx + b)")
    print("=" * 60)

    xs = np.linspace(-3, 3, 100)  # 100 evenly spaced x values from -3 to 3
    m, b = 1.5, -3                # slope and y-intercept

    ys = m * xs + b               # y = 1.5x - 3

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(xs, ys, label=f"y = {m}x + ({b})")

    # Mark two points on the line: y-intercept (0, b) and (2, 0) for this m,b
    ax.plot(0, b, "ro", label=f"y-intercept (0, {b})")
    ax.plot(2, 0, "ro", label="(2, 0) — two right, three up")

    # Horizontal line y = b (m = 0)
    ax.plot(xs, np.full_like(xs, b), "y--", label=f"y = {b} (slope 0)")

    high_school_style(ax)
    ax.set_ylim(-4, 4)
    ax.legend()
    ax.set_title("Linear equation as a graph")

    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")
    else:
        print("Close the plot window to continue (or it runs in background).")

    plt.show()


def section_5_bonus_histogram():
    """Optional: histogram of many dice rolls — shape of random data."""
    rng = np.random.default_rng(99)
    rolls = rng.integers(1, 7, size=10_000)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(rolls, bins=np.arange(0.5, 7.5, 1), edgecolor="black", alpha=0.7)
    ax.set_xticks([1, 2, 3, 4, 5, 6])
    ax.set_xlabel("Dice face")
    ax.set_ylabel("Count")
    ax.set_title("10,000 simulated dice rolls")
    plt.tight_layout()
    plt.show()


# =============================================================================
# CHEAT SHEET (read before you start)
# =============================================================================
CHEAT_SHEET = """
NumPy
  np.array([1,2,3])     list → numeric array
  np.mean(x)            average
  np.dot(a, b)          sum of a[i]*b[i]
  rng.integers(1, 7)    random int in {1..6}
  np.linspace(a, b, n)  n evenly spaced numbers from a to b

Pandas
  pd.DataFrame({...})   table from columns
  df["col"].mean()      column average
  df["col"].value_counts()  how often each value appears

Probability
  P(event) ≈ (times event happened) / (total trials)   [simulation]
  P(event) = (favorable outcomes) / (total outcomes)   [if equally likely]

Matplotlib
  fig, ax = plt.subplots()
  ax.plot(x, y)
  plt.show()
"""


def main() -> None:
    print(CHEAT_SHEET)
    section_1_dice()
    section_2_numpy_basics()
    section_3_pandas_table()
    section_4_probability_rules()

    # Plots open windows — comment out if you only want printed output
    section_5_line_plot(
        save_path="Python_Learning/line_plot_y_equals_mx_plus_b.png"
    )
    # section_5_bonus_histogram()  # uncomment for second plot


if __name__ == "__main__":
    main()
