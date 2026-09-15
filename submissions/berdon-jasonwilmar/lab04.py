"""
Lab 05 - How Accurate is Good Enough?
Approximating y = L sin(theta) using Geometric, Power, Maclaurin, and
Taylor series, with error analysis and an engineering recommendation.
"""

import math
import numpy as np
import matplotlib.pyplot as plt

L = 20.0  # m, structural length

TOLERANCE_PCT = 0.1  # required accuracy: less than 0.1% error
MAX_N_SEARCH = 25     # upper bound when searching for "terms needed"


# =====================================================================
# Helper: render a table as a matplotlib figure (in addition to printing)
# =====================================================================
def show_table(title, col_labels, rows, filename=None):
    """Display a table of strings as a matplotlib figure and (optionally)
    save it to filename. rows is a list of lists of already-formatted
    strings, one inner list per row."""
    n_rows = len(rows)
    n_cols = len(col_labels)

    # Size each column from the widest string it contains (header or data),
    # with a small minimum so single-character columns aren't crushed.
    col_chars = []
    for c in range(n_cols):
        widest = max([len(str(col_labels[c]))] + [len(str(r[c])) for r in rows])
        col_chars.append(max(widest, 4))
    total_chars = sum(col_chars)
    col_widths = [w / total_chars for w in col_chars]

    fig, ax = plt.subplots(figsize=(max(6.0, total_chars * 0.16), 0.7 + 0.4 * n_rows))
    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=col_labels, loc="center",
                      cellLoc="center", colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=20)
    fig.tight_layout()
    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()


# =====================================================================
# PART 1: Geometric series
# =====================================================================
def geometric_sum(x, N):
    """S_N = 1 + x + x^2 + ... + x^N  (partial sum, no closed form used)"""
    total = 0.0
    for k in range(N + 1):
        total += x ** k
    return total


# =====================================================================
# PART 2: Power series
# =====================================================================
def power_series(x, coefficients):
    """Evaluate a0 + a1*x + a2*x^2 + ... given a list of coefficients."""
    result = 0.0
    for k, a_k in enumerate(coefficients):
        result += a_k * (x ** k)
    return result


# =====================================================================
# PART 3: Maclaurin series for sin(theta)
# =====================================================================
def sin_maclaurin(theta, N):
    """N-term Maclaurin approx: theta - theta^3/3! + theta^5/5! - ..."""
    result = 0.0
    for n in range(N):
        sign = (-1) ** n
        factorial = math.factorial(2 * n + 1)
        result += sign * (theta ** (2 * n + 1)) / factorial
    return result


# =====================================================================
# PART 5: Taylor series for sin(theta) centered at a
# =====================================================================
def sin_taylor(theta, a, N):
    """N-term Taylor approximation of sin(theta) centered at angle a (rad)."""
    result = 0.0
    sin_a, cos_a = math.sin(a), math.cos(a)
    h = theta - a
    for n in range(N):
        pattern = n % 4
        if pattern == 0:
            f_deriv = sin_a
        elif pattern == 1:
            f_deriv = cos_a
        elif pattern == 2:
            f_deriv = -sin_a
        else:
            f_deriv = -cos_a
        result += f_deriv * (h ** n) / math.factorial(n)
    return result


# =====================================================================
# Shared data
# =====================================================================
angles_deg = [1, 2, 5, 10, 15, 20, 30]
angles_rad = [math.radians(d) for d in angles_deg]
exact_y = [L * math.sin(t) for t in angles_rad]
a_center_deg = 10
a_center = math.radians(a_center_deg)


def pct_error(approx, exact):
    return abs(approx - exact) / abs(exact) * 100.0


def signed_pct_error(approx, exact):
    return (approx - exact) / exact * 100.0


# =====================================================================
# PART 1 OUTPUT: geometric series investigation
# =====================================================================
def part1_geometric_investigation():
    print("=" * 70)
    print("PART 1: GEOMETRIC SERIES  S_N = 1 + x + x^2 + ... + x^N")
    print("=" * 70)
    x_values = [0.5, 0.8, 0.9]
    n_values = [5, 10, 20, 40]
    table_rows = []
    for x in x_values:
        exact = 1.0 / (1.0 - x)
        print(f"\nx = {x}   (exact 1/(1-x) = {exact:.6f})")
        print(f"{'N':>5} {'Partial Sum':>14} {'Abs Error':>14} {'% Error':>12}")
        for N in n_values:
            s = geometric_sum(x, N)
            err = abs(s - exact)
            pct = err / exact * 100
            print(f"{N:>5} {s:14.6f} {err:14.6e} {pct:12.6g}")
            table_rows.append([f"{x}", f"{N}", f"{s:.6f}", f"{err:.3e}", f"{pct:.4g}"])
    print("\nObservation: larger |x| converges more slowly -- each extra term")
    print("shrinks the remainder by a factor of x, so x=0.9 needs far more")
    print("terms than x=0.5 to reach the same accuracy.\n")
    show_table("Part 1: Geometric Series Partial Sums",
               ["x", "N", "Partial Sum", "Abs Error", "% Error"],
               table_rows, filename="table_part1_geometric.png")


# =====================================================================
# PART 2 OUTPUT: power series demo
# =====================================================================
def part2_power_series_demo():
    print("=" * 70)
    print("PART 2: POWER SERIES  P_N(x) = a0 + a1 x + a2 x^2 + ...")
    print("=" * 70)
    # Demonstrate that the Maclaurin sine series is just a power series
    # with coefficients 0, 1, 0, -1/3!, 0, 1/5!, ...
    coeffs = [0.0, 1.0, 0.0, -1 / math.factorial(3), 0.0, 1 / math.factorial(5)]
    x = math.radians(10)
    exact = math.sin(x)
    print(f"Evaluating a 6-coefficient power series (sin's Maclaurin coeffs)")
    print(f"at x = 10 deg: P(x) = {power_series(x, coeffs):.6f}   vs. math.sin = {exact:.6f}")
    print("This confirms sin(theta)'s Maclaurin series is a special case of a")
    print("general power series: only the odd-power coefficients are nonzero.\n")

    print(f"{'k':>3} {'a_k':>14} {'Partial P_k(x)':>16} {'% Error':>12}")
    table_rows = []
    for k in range(len(coeffs)):
        partial = power_series(x, coeffs[:k + 1])
        pct = abs(partial - exact) / exact * 100 if exact != 0 else 0.0
        print(f"{k:>3} {coeffs[k]:14.6f} {partial:16.8f} {pct:12.6g}")
        table_rows.append([f"{k}", f"{coeffs[k]:.6f}", f"{partial:.8f}", f"{pct:.4g}"])
    print()
    show_table("Part 2: Power Series Coefficients and Partial Sums at x = 10 deg",
               ["k", "a_k", "Partial P_k(x)", "% Error"],
               table_rows, filename="table_part2_power_series.png")


# =====================================================================
# PART 3 OUTPUT: sin(10 deg) approximation vs number of terms
# =====================================================================
def part3_maclaurin_investigation():
    print("=" * 70)
    print("PART 3: MACLAURIN SERIES FOR sin(theta), theta = 10 deg")
    print("=" * 70)
    theta = math.radians(10)
    exact = math.sin(theta)
    print(f"{'N terms':>8} {'Approx sin':>14} {'Abs Error':>14} {'% Error':>12}")
    table_rows = []
    for N in range(1, 5):
        approx = sin_maclaurin(theta, N)
        err = abs(approx - exact)
        pct = err / exact * 100
        print(f"{N:>8} {approx:14.8f} {err:14.2e} {pct:12.6g}")
        table_rows.append([f"{N}", f"{approx:.8f}", f"{err:.3e}", f"{pct:.4g}"])
    print()
    show_table("Part 3: Maclaurin Approximation of sin(10 deg)",
               ["N terms", "Approx sin", "Abs Error", "% Error"],
               table_rows, filename="table_part3_maclaurin10.png")


# =====================================================================
# PART 4 OUTPUT: engineering tables for y = L sin(theta), Maclaurin
# =====================================================================
def part4_maclaurin_engineering_tables():
    print("=" * 70)
    print("PART 4: MACLAURIN APPROXIMATIONS FOR y = L sin(theta), L = 20 m")
    print("=" * 70)
    print(f"{'Angle':>5} {'Exact y':>12} {'N=1':>12} {'N=2':>12} {'N=3':>12} {'N=4':>12}")
    value_rows = []
    for d, th, yex in zip(angles_deg, angles_rad, exact_y):
        vals = [L * sin_maclaurin(th, N) for N in range(1, 5)]
        print(f"{d:>5} {yex:12.6f} {vals[0]:12.6f} {vals[1]:12.6f} {vals[2]:12.6f} {vals[3]:12.6f}")
        value_rows.append([f"{d}", f"{yex:.6f}"] + [f"{v:.6f}" for v in vals])
    show_table("Part 4: Maclaurin Approximations of y = L sin(theta)",
               ["Angle (deg)", "Exact y", "N=1", "N=2", "N=3", "N=4"],
               value_rows, filename="table_part4_maclaurin_values.png")

    print("\nMACLAURIN PERCENT ERRORS")
    print(f"{'Angle':>5} {'N=1':>12} {'N=2':>12} {'N=3':>12} {'N=4':>12}")
    error_rows = []
    for d, th, yex in zip(angles_deg, angles_rad, exact_y):
        errs = [pct_error(L * sin_maclaurin(th, N), yex) for N in range(1, 5)]
        print(f"{d:>5} {errs[0]:12.6g} {errs[1]:12.6g} {errs[2]:12.6g} {errs[3]:12.6g}")
        error_rows.append([f"{d}"] + [f"{e:.4g}" for e in errs])
    print()
    show_table("Part 4: Maclaurin Percent Errors",
               ["Angle (deg)", "N=1", "N=2", "N=3", "N=4"],
               error_rows, filename="table_part4_maclaurin_errors.png")


# =====================================================================
# PART 5 OUTPUT: Taylor tables centered at 10 deg
# =====================================================================
def part5_taylor_engineering_tables():
    print("=" * 70)
    print(f"PART 5: TAYLOR APPROXIMATIONS CENTERED AT {a_center_deg} DEGREES")
    print("=" * 70)
    print(f"{'Angle':>5} {'Exact y':>12} {'N=1':>12} {'N=2':>12} {'N=3':>12} {'N=4':>12}")
    value_rows = []
    for d, th, yex in zip(angles_deg, angles_rad, exact_y):
        vals = [L * sin_taylor(th, a_center, N) for N in range(1, 5)]
        print(f"{d:>5} {yex:12.6f} {vals[0]:12.6f} {vals[1]:12.6f} {vals[2]:12.6f} {vals[3]:12.6f}")
        value_rows.append([f"{d}", f"{yex:.6f}"] + [f"{v:.6f}" for v in vals])
    show_table(f"Part 5: Taylor Approximations of y = L sin(theta), centered at {a_center_deg} deg",
               ["Angle (deg)", "Exact y", "N=1", "N=2", "N=3", "N=4"],
               value_rows, filename="table_part5_taylor_values.png")

    print("\nTAYLOR PERCENT ERRORS (signed) CENTERED AT 10 DEGREES")
    print(f"{'Angle':>5} {'N=1':>12} {'N=2':>12} {'N=3':>12} {'N=4':>12}")
    error_rows = []
    for d, th, yex in zip(angles_deg, angles_rad, exact_y):
        errs = [signed_pct_error(L * sin_taylor(th, a_center, N), yex) for N in range(1, 5)]
        print(f"{d:>5} {errs[0]:12.6g} {errs[1]:12.6g} {errs[2]:12.6g} {errs[3]:12.6g}")
        error_rows.append([f"{d}"] + [f"{e:.4g}" for e in errs])
    print()
    show_table(f"Part 5: Taylor Percent Errors (signed), centered at {a_center_deg} deg",
               ["Angle (deg)", "N=1", "N=2", "N=3", "N=4"],
               error_rows, filename="table_part5_taylor_errors.png")


# =====================================================================
# PART 6 OUTPUT, Task 1: minimum terms to meet 0.1% tolerance
# =====================================================================
def terms_needed(theta, series_func, tol_pct=TOLERANCE_PCT, max_n=MAX_N_SEARCH):
    """Return the smallest N (>=1) for which series_func(theta, N) is within
    tol_pct percent of the true sin(theta). Returns None if not reached
    within max_n terms."""
    exact = math.sin(theta)
    for N in range(1, max_n + 1):
        approx = series_func(theta, N)
        if exact != 0 and abs(approx - exact) / abs(exact) * 100.0 <= tol_pct:
            return N
    return None


def part6_task1_terms_for_tolerance():
    print("=" * 70)
    print(f"PART 6 (Task 1): MIN TERMS FOR < {TOLERANCE_PCT}% ERROR")
    print("=" * 70)
    print(f"{'Angle':>5} {'Maclaurin N':>13} {'Taylor(a=10) N':>16}")
    table_rows = []
    for d, th in zip(angles_deg, angles_rad):
        n_mac = terms_needed(th, lambda t, N: sin_maclaurin(t, N))
        n_tay = terms_needed(th, lambda t, N: sin_taylor(t, a_center, N))
        n_mac_s = n_mac if n_mac is not None else f">{MAX_N_SEARCH}"
        n_tay_s = n_tay if n_tay is not None else f">{MAX_N_SEARCH}"
        print(f"{d:>5} {n_mac_s:>13} {n_tay_s:>16}")
        table_rows.append([f"{d}", f"{n_mac_s}", f"{n_tay_s}"])
    print()
    show_table(f"Part 6: Min Terms Needed for < {TOLERANCE_PCT}% Error",
               ["Angle (deg)", "Maclaurin N", "Taylor(a=10) N"],
               table_rows, filename="table_part6_terms_needed.png")


# =====================================================================
# PART 6 OUTPUT, Task 2: critical angle for 1-term small-angle approx
# =====================================================================
def part6_task2_critical_angle(tol_pct=TOLERANCE_PCT):
    print("=" * 70)
    print(f"PART 6 (Task 2): CRITICAL ANGLE FOR sin(theta) ~= theta (< {tol_pct}% error)")
    print("=" * 70)
    critical_deg = None
    for tenth_deg in range(1, 900):  # sweep 0.1 deg steps up to 90 deg
        deg = tenth_deg / 10.0
        th = math.radians(deg)
        exact = math.sin(th)
        approx = sin_maclaurin(th, 1)  # 1-term Maclaurin = theta itself
        err = abs(approx - exact) / exact * 100.0
        if err > tol_pct:
            critical_deg = deg
            break
    if critical_deg:
        print(f"The 1-term approximation sin(theta) ~= theta exceeds {tol_pct}% error")
        print(f"at approximately theta = {critical_deg:.1f} degrees.\n")
    else:
        print("Tolerance not exceeded within the sweep range.\n")
    return critical_deg


# =====================================================================
# PLOT 1: Convergence plot -- % error vs number of terms, per angle
# =====================================================================
def plot_convergence():
    N_range = range(1, 9)
    fig, ax = plt.subplots(figsize=(8, 6))
    for d, th in zip(angles_deg, angles_rad):
        exact = math.sin(th)
        errs = [pct_error(sin_maclaurin(th, N), exact) for N in N_range]
        ax.semilogy(list(N_range), errs, marker="o", label=f"{d} deg")
    ax.axhline(TOLERANCE_PCT, color="black", linestyle="--", linewidth=1,
               label=f"{TOLERANCE_PCT}% tolerance")
    ax.set_xlabel("Number of terms, N")
    ax.set_ylabel("Percent error (log scale)")
    ax.set_title("Maclaurin Series Convergence for sin(theta)")
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig("convergence_plot.png", dpi=150)
    plt.show()


# =====================================================================
# PLOT 2: Function comparison -- exact vs Maclaurin vs Taylor
# =====================================================================
def plot_function_comparison():
    theta_deg_fine = np.linspace(0, 40, 400)
    theta_rad_fine = np.radians(theta_deg_fine)
    exact_fine = np.sin(theta_rad_fine)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    # Left: Maclaurin
    axes[0].plot(theta_deg_fine, exact_fine, "k-", linewidth=2, label="exact sin")
    for N in [1, 2, 3, 4]:
        approx = [sin_maclaurin(t, N) for t in theta_rad_fine]
        axes[0].plot(theta_deg_fine, approx, linestyle="--", label=f"N={N}")
    axes[0].set_title("Maclaurin (centered at 0 deg)")
    axes[0].set_xlabel("theta (deg)")
    axes[0].set_ylabel("sin(theta)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    # Right: Taylor centered at 10 deg
    axes[1].plot(theta_deg_fine, exact_fine, "k-", linewidth=2, label="exact sin")
    for N in [1, 2, 3, 4]:
        approx = [sin_taylor(t, a_center, N) for t in theta_rad_fine]
        axes[1].plot(theta_deg_fine, approx, linestyle="--", label=f"N={N}")
    axes[1].axvline(a_center_deg, color="gray", linestyle=":", linewidth=1)
    axes[1].set_title(f"Taylor (centered at {a_center_deg} deg)")
    axes[1].set_xlabel("theta (deg)")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)

    fig.suptitle("Exact sin(theta) vs. Series Approximations")
    fig.tight_layout()
    fig.savefig("function_comparison_plot.png", dpi=150)
    plt.show()


# =====================================================================
# PLOT 3: Error comparison -- Maclaurin vs Taylor, abs and percent error
# =====================================================================
def plot_error_comparison(N=3):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    abs_err_mac = [abs(L * sin_maclaurin(th, N) - yex)
                   for th, yex in zip(angles_rad, exact_y)]
    abs_err_tay = [abs(L * sin_taylor(th, a_center, N) - yex)
                   for th, yex in zip(angles_rad, exact_y)]
    pct_err_mac = [pct_error(L * sin_maclaurin(th, N), yex)
                   for th, yex in zip(angles_rad, exact_y)]
    pct_err_tay = [pct_error(L * sin_taylor(th, a_center, N), yex)
                   for th, yex in zip(angles_rad, exact_y)]

    x = np.arange(len(angles_deg))
    width = 0.35

    axes[0].bar(x - width / 2, abs_err_mac, width, label="Maclaurin")
    axes[0].bar(x + width / 2, abs_err_tay, width, label="Taylor (a=10 deg)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"{d} deg" for d in angles_deg])
    axes[0].set_ylabel("Absolute error in y (m)")
    axes[0].set_title(f"Absolute Error, N={N} terms")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3, axis="y")

    axes[1].bar(x - width / 2, pct_err_mac, width, label="Maclaurin")
    axes[1].bar(x + width / 2, pct_err_tay, width, label="Taylor (a=10 deg)")
    axes[1].axhline(TOLERANCE_PCT, color="black", linestyle="--", linewidth=1,
                     label=f"{TOLERANCE_PCT}% tolerance")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f"{d} deg" for d in angles_deg])
    axes[1].set_ylabel("Percent error (%)")
    axes[1].set_title(f"Percent Error, N={N} terms")
    axes[1].set_yscale("log")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3, axis="y")

    fig.suptitle("Maclaurin vs. Taylor Error Comparison")
    fig.tight_layout()
    fig.savefig("error_comparison_plot.png", dpi=150)
    plt.show()


# =====================================================================
# PART 7 OUTPUT: written engineering recommendation
# =====================================================================
def part7_recommendation(critical_deg):
    print("=" * 70)
    print("PART 7: FINAL ENGINEERING RECOMMENDATION")
    print("=" * 70)
    print(f"""
For angles up to 30 degrees, a Maclaurin series is the simplest and cheapest
choice: it needs no extra evaluation point and its error stays below
{TOLERANCE_PCT}% for a modest number of terms (see the "MIN TERMS" table above),
because theta stays small relative to the origin and each added term shrinks
the remainder quickly (alternating series with rapidly-growing factorials).

If the work is concentrated near one particular angle far from zero (e.g.
surveying repeatedly near 10 degrees), a Taylor series centered at that angle
converges just as fast with fewer terms locally, but loses accuracy quickly
outside a narrow band around the center -- so it is only worth the extra
bookkeeping (storing sin(a), cos(a)) when the angle of interest is fixed and
known in advance.

The single-term small-angle approximation sin(theta) ~= theta is only
trustworthy below about {critical_deg:.1f} degrees for {TOLERANCE_PCT}% accuracy;
beyond that a civil engineer should add at least one more term or switch to
math.sin() directly, which is exact to machine precision and effectively free
computationally on any modern system.

Recommendation: use math.sin() when it is available (it costs nothing and is
exact). The series approximations are valuable here to demonstrate *why*
small-angle and locally-linearized formulas used in hand calculations and
older engineering references are valid only within a bounded angular range,
and to quantify that range and the resulting error for a documented design
justification.
""")


# =====================================================================
# Main driver
# =====================================================================
if __name__ == "__main__":
    part1_geometric_investigation()
    part2_power_series_demo()
    part3_maclaurin_investigation()
    part4_maclaurin_engineering_tables()
    part5_taylor_engineering_tables()
    part6_task1_terms_for_tolerance()
    critical_angle = part6_task2_critical_angle()

    plot_convergence()
    plot_function_comparison()
    plot_error_comparison()

    part7_recommendation(critical_angle)

    print("Saved plots: convergence_plot.png, function_comparison_plot.png, "
          "error_comparison_plot.png")
