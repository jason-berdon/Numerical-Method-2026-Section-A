import math
import json
import webbrowser
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# =================================================================
# EXERCISE 1: Convergence of (1 + 1/n)^n to e
# =================================================================
periods = [
    ("yearly",              1),
    ("twice a year",        2),
    ("quarterly",           4),
    ("monthly",             12),
    ("weekly",              52),
    ("daily",               365),
    ("hourly",              365 * 24),
    ("every minute",        365 * 24 * 60),
    ("every second",        365 * 24 * 60 * 60),
    ("every millisecond",   365 * 24 * 60 * 60 * 1_000),
    ("every microsecond",   365 * 24 * 60 * 60 * 1_000_000),
    ("every nanosecond",    365 * 24 * 60 * 60 * 1_000_000_000),
]
labels1 = [p[0] for p in periods]
ns = np.array([p[1] for p in periods], dtype=float)

values1 = np.exp(ns * np.log1p(1.0 / ns))
errors1 = np.abs(values1 - math.e)

print("=" * 60)
print("EXERCISE 1: (1 + 1/n)^n -> e")
print("=" * 60)
print(f"{'How often':<20}{'n':>18}{'(1+1/n)^n':>18}")
for lbl, n, v in zip(labels1, ns, values1):
    print(f"{lbl:<20}{int(n):>18,}{v:>18.6f}")
print(f"\ne = {math.e:.6f}\n")

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), num="Figure 1")
fig1.suptitle("Exercise 1: Convergence of (1 + 1/n)^n to e", fontsize=13, fontweight="bold")

bars = ax1.bar(labels1, values1, color="#1f77ff", edgecolor="black", linewidth=0.5)
ax1.axhline(math.e, color="red", linestyle="--", linewidth=1.2, label=f"e = {math.e:.6f}")
ax1.set_title("Value per compounding period")
ax1.set_ylabel("(1 + 1/n)^n")
ax1.set_ylim(1.8, 3.0)
ax1.set_xticks(range(len(labels1)))
ax1.set_xticklabels(labels1, rotation=45, ha="right")
ax1.legend(loc="lower right")
for bar, v in zip(bars, values1):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
              f"{v:.6f}", rotation=90, ha="center", va="bottom", fontsize=7)

plot_errors1 = np.where(errors1 > 0, errors1, 1e-16)
ax2.bar(labels1, plot_errors1, color="orange", edgecolor="black", linewidth=0.5)
ax2.set_yscale("log")
ax2.set_title("Error shrinks like e/(2n)")
ax2.set_ylabel("|(1 + 1/n)^n - e|  (log scale)")
ax2.set_xticks(range(len(labels1)))
ax2.set_xticklabels(labels1, rotation=45, ha="right")

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("./exercise1_convergence_to_e.png", dpi=150)
print("Saved -> exercise1_convergence_to_e.png\n")
plt.show()

# =================================================================
# EXERCISE 2: (a^h - 1)/h settling to ln(a)
# =================================================================
h_values = [0.1, 0.01, 0.001, 0.0001, 1e-5, 1e-6, 1e-7]
bases = {"a=2": 2.0, "a=e": math.e, "a=3": 3.0}
colors2 = {"a=2": "#1f4fd8", "a=e": "#1fa22e", "a=3": "#d81f1f"}

quotients = {name: [(a ** h - 1) / h for h in h_values] for name, a in bases.items()}
limits = {name: math.log(a) for name, a in bases.items()}

print("=" * 60)
print("EXERCISE 2: (a^h - 1)/h -> ln(a)   (tolerance 1e-6)")
print("=" * 60)
print(f"{'h':>10}{'a=2':>12}{'a=2.71828...':>15}{'a=3':>12}")
for i, h in enumerate(h_values):
    print(f"{h:>10}{quotients['a=2'][i]:>12.4f}{quotients['a=e'][i]:>15.4f}{quotients['a=3'][i]:>12.4f}")
print(f"{'settles at':>10}{limits['a=2']:>12.4f}{limits['a=e']:>15.4f}{limits['a=3']:>12.4f}\n")

fig2, ax3 = plt.subplots(figsize=(12, 6), num="Figure 2")
fig2.suptitle("Exercise 2: (a^h - 1)/h settling to ln(a)", fontsize=13, fontweight="bold")
ax3.set_title("Bars: difference quotient per h.  Dashed lines: the limit ln(a).", fontsize=10)

x = np.arange(len(h_values))
width = 0.25
for i, name in enumerate(bases):
    offset = (i - 1) * width
    ax3.bar(x + offset, quotients[name], width,
            label=f"{name}  (ln a = {limits[name]:.4f})",
            color=colors2[name], edgecolor="black", linewidth=0.5)
    ax3.axhline(limits[name], color=colors2[name], linestyle="--", linewidth=1, alpha=0.7)
ax3.set_xticks(x)
ax3.set_xticklabels([f"h = {h:g}" for h in h_values])
ax3.set_ylabel("(a^h - 1)/h")
ax3.set_ylim(0.6, 1.25)
ax3.legend(loc="upper right")

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig("./exercise2_difference_quotient.png", dpi=150)
print("Saved -> exercise2_difference_quotient.png\n")
plt.show()

# =================================================================
# EXERCISE 3: Partial sums of e^x = sum x^n/n!  (x = 1)
# =================================================================
checkpoints = [1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 1000, 10000]
S, term, n = 0.0, 1.0, 0
results = {}
checkpoint_set = set(checkpoints)
max_N = max(checkpoints)
while n <= max_N:
    S += term
    if n in checkpoint_set:
        results[n] = S
    n += 1
    term /= n

partial_sums = np.array([results[n] for n in checkpoints])
errors3 = np.abs(partial_sums - math.e)
correct_digits = -np.log10(np.maximum(errors3, 1e-16))

print("=" * 60)
print("EXERCISE 3: e^x = sum x^n/n!  (x = 1), up to N = 10,000")
print("=" * 60)
print(f"{'N':>8}{'S_N':>16}{'|S_N - e|':>16}{'correct digits':>16}")
for nck, s, e_, d in zip(checkpoints, partial_sums, errors3, correct_digits):
    print(f"{nck:>8}{s:>16.10f}{e_:>16.2e}{d:>16.1f}")
print(f"\ne = {math.e:.10f}\n")

xlabels3 = [str(n) for n in checkpoints]

fig3, (ax4, ax5) = plt.subplots(1, 2, figsize=(14, 6), num="Figure 3")
fig3.suptitle("Exercise 3: e^x = sum x^n / n!  (x = 1), summation up to N = 10,000 terms",
              fontsize=12, fontweight="bold")

ax4.bar(xlabels3, partial_sums, color="#7d3fd8", edgecolor="black", linewidth=0.5)
ax4.axhline(math.e, color="red", linestyle="--", linewidth=1.2, label=f"e = {math.e:.6f}")
ax4.set_title("Histogram of the partial sums")
ax4.set_ylabel("S_N = sum(x^n/n!)")
ax4.set_ylim(0, 3.1)
ax4.legend(loc="lower right")
for i, s in enumerate(partial_sums):
    ax4.text(i, s + 0.03, f"{s:.6f}", rotation=90, ha="center", va="bottom", fontsize=7)

ax5.plot(checkpoints, errors3, "o-", color="black", markerfacecolor="none")
ax5.set_xscale("log")
ax5.set_yscale("log")
ax5.set_title("How many correct digits each N buys (log-log)")
ax5.set_xlabel("number of terms N in the summation (log scale)")
ax5.set_ylabel("|S_N - e|  (log scale)")

band_colors = []
for d in correct_digits:
    if d < 2:
        c = "red"
    elif d < 6:
        c = "orange"
    elif d < 14:
        c = "green"
    else:
        c = "blue"
    band_colors.append(c)

for x_, y_, d, c in zip(checkpoints, errors3, correct_digits, band_colors):
    ax5.plot(x_, y_, "o", color=c, markersize=6)
    ax5.annotate(f"{d:.0f} digits", (x_, y_), textcoords="offset points",
                 xytext=(0, 8), ha="center", fontsize=7, color=c)

ax5.axhspan(1e-16, 3e-16, color="steelblue", alpha=0.15)
ax5.text(checkpoints[3], 2e-16, "machine precision floor (~1e-16)",
          fontsize=7, color="steelblue", va="center")

legend_elems = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="red", label="rough (< 2 digits)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="orange", label="engineering (2-6 digits)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="green", label="high precision (6-14 digits)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="blue", label="machine precision (>14 digits)"),
]
ax5.legend(handles=legend_elems, loc="upper right", fontsize=7)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig("./exercise3_taylor_series_partial_sums.png", dpi=150)
print("Saved -> exercise3_taylor_series_partial_sums.png")
plt.show()

ex1_data = {
    "labels": labels1,
    "values": [round(v, 6) for v in values1.tolist()],
}

ex2_data = {
    "hLabels": [f"h={h:g}" for h in h_values],
    "a2": [round(v, 4) for v in quotients["a=2"]],
    "ae": [round(v, 4) for v in quotients["a=e"]],
    "a3": [round(v, 4) for v in quotients["a=3"]],
    "lim2": limits["a=2"],
    "lime": limits["a=e"],
    "lim3": limits["a=3"],
}

ex3_data = {
    "N": checkpoints,
    "err": [float(e) for e in errors3],
    "digits": [round(float(d), 1) for d in correct_digits],
}

E_CONST = math.e

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Three Roads to e</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --board:      #16261f;
    --board-2:    #1c332a;
    --chalk:      #eae3d3;
    --chalk-dim:  #b9c2b8;
    --rail:       #3a5346;
    --gold:       #d9a441;
    --gold-dim:   #a9803a;
    --line2:      #6fa6c9;
    --line3:      #c96f6f;
    --linee:      #d9a441;
    --band-red:   #c96f6f;
    --band-orange:#d9a441;
    --band-green: #7fb08a;
    --band-blue:  #6fa6c9;
    --serif: 'Spectral', Georgia, serif;
    --mono: 'JetBrains Mono', ui-monospace, monospace;
  }

  *{ box-sizing:border-box; }
  html{ scroll-behavior:smooth; }
  body{
    margin:0;
    background:var(--board);
    color:var(--chalk);
    font-family:var(--serif);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }

  body::before{
    content:"";
    position:fixed; inset:0;
    pointer-events:none;
    background-image:
      radial-gradient(rgba(234,227,211,0.025) 1px, transparent 1px);
    background-size: 3px 3px;
    z-index:0;
  }

  .wrap{ position:relative; z-index:1; }

  a{ color:var(--gold); }

  .rail{
    max-width:760px;
    margin:0 auto;
    padding:0 28px;
  }

  .hero{
    min-height:100svh;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:60px 24px;
    border-bottom:1px solid var(--rail);
  }
  .hero-e{
    font-size:clamp(96px, 22vw, 220px);
    font-weight:400;
    font-style:italic;
    line-height:1;
    color:var(--chalk);
    filter: drop-shadow(0 0 18px rgba(217,164,65,0.12));
    opacity:0;
    animation: chalkIn 1.1s ease-out 0.15s forwards;
  }
  @keyframes chalkIn{
    from{ opacity:0; transform:translateY(10px) scale(0.97); }
    to{ opacity:1; transform:translateY(0) scale(1); }
  }
  .hero-digits{
    margin-top:6px;
    font-family:var(--mono);
    font-size:clamp(18px,4vw,28px);
    color:var(--gold);
    letter-spacing:0.02em;
    min-height:1.4em;
  }
  .hero-digits .cursor{
    display:inline-block;
    width:0.5ch;
    animation: blink 1s step-end infinite;
  }
  @keyframes blink{ 50%{ opacity:0; } }
  .hero-sub{
    max-width:520px;
    margin-top:28px;
    color:var(--chalk-dim);
    font-size:17px;
    opacity:0;
    animation: fadeUp 0.9s ease-out 1.4s forwards;
  }
  @keyframes fadeUp{
    from{ opacity:0; transform:translateY(8px); }
    to{ opacity:1; transform:translateY(0); }
  }
  .hero-nav{
    display:flex;
    gap:10px;
    margin-top:44px;
    opacity:0;
    animation: fadeUp 0.9s ease-out 1.7s forwards;
  }
  .hero-nav a{
    font-family:var(--mono);
    font-size:12.5px;
    color:var(--chalk-dim);
    text-decoration:none;
    border:1px solid var(--rail);
    padding:7px 13px;
    border-radius:2px;
    transition:border-color .2s, color .2s;
  }
  .hero-nav a:hover{ border-color:var(--gold-dim); color:var(--gold); }

  section.piece{
    padding:96px 0 88px;
    border-bottom:1px solid var(--rail);
  }
  section.piece:last-of-type{ border-bottom:none; }

  .kicker{
    font-family:var(--mono);
    font-size:13px;
    color:var(--gold-dim);
    margin:0 0 10px;
  }
  h2{
    font-family:var(--serif);
    font-weight:500;
    font-size:clamp(26px,4vw,34px);
    margin:0 0 18px;
    color:var(--chalk);
  }
  h2 em{ font-style:italic; color:var(--gold); }
  .lede{
    color:var(--chalk-dim);
    font-size:16.5px;
    max-width:64ch;
    margin:0 0 30px;
  }
  .lede .expr{ color:var(--chalk); font-family:var(--mono); font-size:0.95em; }

  .figure{
    background:var(--board-2);
    border:1px solid var(--rail);
    border-radius:3px;
    padding:22px 18px 14px;
    margin-bottom:20px;
  }
  .figure canvas{ width:100%; display:block; }
  .figure-caption{
    font-family:var(--mono);
    font-size:12px;
    color:var(--chalk-dim);
    margin-top:10px;
    display:flex;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:6px;
  }
  .figure-caption .val{ color:var(--gold); }

  .legend{
    display:flex;
    gap:18px;
    flex-wrap:wrap;
    font-family:var(--mono);
    font-size:12px;
    color:var(--chalk-dim);
    margin-top:8px;
  }
  .legend span{ display:inline-flex; align-items:center; gap:6px; }
  .swatch{ width:9px; height:9px; border-radius:50%; display:inline-block; }

  .note{
    font-size:15px;
    color:var(--chalk-dim);
    max-width:64ch;
    margin-top:22px;
  }
  .note strong{ color:var(--chalk); font-weight:600; }

  footer{
    padding:60px 0 90px;
    text-align:center;
    color:var(--chalk-dim);
    font-family:var(--mono);
    font-size:12.5px;
  }
  footer .e{ color:var(--gold); font-family:var(--serif); font-style:italic; }

  @media (prefers-reduced-motion: reduce){
    *{ animation-duration:0.01ms !important; animation-iteration-count:1 !important; transition-duration:0.01ms !important; }
  }

  @media (max-width:600px){
    .rail{ padding:0 18px; }
    section.piece{ padding:64px 0 56px; }
    .figure{ padding:16px 12px 12px; }
  }
</style>
</head>
<body>
<div class="wrap">

  <section class="hero">
    <div class="hero-e">e</div>
    <div class="hero-digits" id="heroDigits">2.<span id="digitStream"></span><span class="cursor">|</span></div>
    <p class="hero-sub">One constant, three different roads to it — compound interest pushed to its limit, a slope measured ever more finely, and an infinite sum that stops moving. Scroll to watch each one arrive.</p>
    <nav class="hero-nav">
      <a href="#ex1">01 · Compounding</a>
      <a href="#ex2">02 · Slope</a>
      <a href="#ex3">03 · Series</a>
    </nav>
  </section>

  <section class="piece" id="ex1">
    <div class="rail">
      <p class="kicker">Exercise 1 — the limit definition</p>
      <h2>Compounding, pushed until it can't be pushed further</h2>
      <p class="lede">
        Compound interest once a year on a 100% rate doubles your money. Compound it continuously —
        every nanosecond — and growth stops accelerating. It settles.
        <span class="expr">(1 + 1/n)ⁿ → e</span> as n grows without bound.
      </p>
      <div class="figure">
        <canvas id="c1" width="1400" height="620"></canvas>
        <div class="figure-caption">
          <span id="c1cap">watching yearly compounding…</span>
          <span class="val" id="c1val"></span>
        </div>
      </div>
      <p class="note">Notice how little ground is left to cover after <strong>hourly</strong> compounding — the value is already
      within 0.0002 of e. Compounding faster than that buys almost nothing more.</p>
    </div>
  </section>

  <section class="piece" id="ex2">
    <div class="rail">
      <p class="kicker">Exercise 2 — the derivative definition</p>
      <h2>Shrink the step, and a slope reveals <em>ln(a)</em></h2>
      <p class="lede">
        The expression <span class="expr">(aʰ − 1) / h</span> is the average slope of aˣ over a tiny step h.
        As h shrinks toward zero, that average slope becomes the instantaneous one — and it settles at
        <span class="expr">ln(a)</span>. For a = e, the slope settles at exactly 1: e is the one base whose
        curve rises at its own value.
      </p>
      <div class="figure">
        <canvas id="c2" width="1400" height="620"></canvas>
        <div class="figure-caption">
          <span id="c2cap">h = 0.1</span>
          <span class="val" id="c2val"></span>
        </div>
        <div class="legend">
          <span><i class="swatch" style="background:var(--line2)"></i>a = 2 → ln 2 ≈ 0.6931</span>
          <span><i class="swatch" style="background:var(--linee)"></i>a = e → ln e = 1</span>
          <span><i class="swatch" style="background:var(--line3)"></i>a = 3 → ln 3 ≈ 1.0986</span>
        </div>
      </div>
      <p class="note">Only <strong>a = e</strong> lands exactly on 1 — that's the defining property mathematicians actually mean
      when they call e "the natural base."</p>
    </div>
  </section>

  <section class="piece" id="ex3">
    <div class="rail">
      <p class="kicker">Exercise 3 — the series definition</p>
      <h2>An infinite sum that gives up moving</h2>
      <p class="lede">
        <span class="expr">eˣ = Σ xⁿ⁄n!</span> — at x = 1 this is a sum of shrinking fractions:
        1 + 1 + 1/2 + 1/6 + 1/24 + … Each new term is added, the running total edges closer to e,
        and then — around N = 20 — floating-point arithmetic simply runs out of precision to give.
      </p>
      <div class="figure">
        <canvas id="c3" width="1400" height="680"></canvas>
        <div class="figure-caption">
          <span id="c3cap">N = 1</span>
          <span class="val" id="c3val"></span>
        </div>
        <div class="legend">
          <span><i class="swatch" style="background:var(--band-red)"></i>rough (&lt;2 digits)</span>
          <span><i class="swatch" style="background:var(--band-orange)"></i>engineering (2–6)</span>
          <span><i class="swatch" style="background:var(--band-green)"></i>high precision (6–14)</span>
          <span><i class="swatch" style="background:var(--band-blue)"></i>machine limit (&gt;14)</span>
        </div>
      </div>
      <p class="note">By N = 20 the sum has already found all 15–16 digits a standard double can hold.
      Adding the 10,000th term changes nothing — the error curve goes flat against the
      <strong>machine-precision floor</strong> near 10⁻¹⁶.</p>
    </div>
  </section>

  <footer>
    generated from a convergence study of <span class="e">e</span> — three limits, one constant
  </footer>

</div>

<script>
(function(){
  "use strict";

  function ease(t){ return 1 - Math.pow(1 - t, 3); }

  (function heroTyper(){
    const digits = "__E_DIGITS__".split("");
    const el = document.getElementById('digitStream');
    let i = 0;
    function step(){
      if(i < digits.length){
        el.textContent += digits[i];
        i++;
        setTimeout(step, 90 + Math.random()*70);
      }
    }
    setTimeout(step, 500);
  })();

  function onEnter(el, cb){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(e.isIntersecting){
          cb();
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });
    io.observe(el);
  }

  // ---- data injected from the Python script ----
  const ex1 = __EX1_JSON__;
  const ex2 = __EX2_JSON__;
  const ex3 = __EX3_JSON__;
  const E = __E_CONST__;

  function drawEx1(cv, progressPerBar){
    const ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    ctx.clearRect(0,0,W,H);

    const padL = 70, padR = 30, padT = 30, padB = 120;
    const plotW = W - padL - padR, plotH = H - padT - padB;
    const yMin = 1.8, yMax = 3.0;
    const n = ex1.labels.length;
    const gap = 14;
    const barW = (plotW - gap*(n-1)) / n;

    function yPix(v){ return padT + plotH * (1 - (v - yMin)/(yMax - yMin)); }

    ctx.strokeStyle = 'rgba(234,227,211,0.08)';
    ctx.lineWidth = 1;
    ctx.font = '20px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(234,227,211,0.45)';
    for(let v = 2.0; v <= 3.0; v += 0.2){
      const y = yPix(v);
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
      ctx.fillText(v.toFixed(1), 14, y+6);
    }

    for(let i=0;i<n;i++){
      const p = Math.max(0, Math.min(1, progressPerBar(i)));
      const val = yMin + (ex1.values[i]-yMin) * ease(p);
      const x = padL + i*(barW+gap);
      const yTop = yPix(val);
      const yBase = yPix(yMin);
      const grad = ctx.createLinearGradient(0,yTop,0,yBase);
      grad.addColorStop(0, '#e0b358');
      grad.addColorStop(1, '#9c7226');
      ctx.fillStyle = p > 0 ? grad : 'rgba(234,227,211,0.06)';
      ctx.fillRect(x, yTop, barW, yBase - yTop);

      if(p > 0.05){
        ctx.save();
        ctx.translate(x + barW/2, yTop - 8);
        ctx.rotate(-Math.PI/2.4);
        ctx.font = '18px "JetBrains Mono", monospace';
        ctx.fillStyle = 'rgba(234,227,211,0.8)';
        ctx.textAlign = 'left';
        ctx.fillText(val.toFixed(6), 0, 0);
        ctx.restore();
      }

      ctx.save();
      ctx.translate(x + barW/2, H - padB + 18);
      ctx.rotate(-Math.PI/5);
      ctx.font = '19px "Spectral", serif';
      ctx.fillStyle = 'rgba(234,227,211,0.55)';
      ctx.textAlign = 'right';
      ctx.fillText(ex1.labels[i], 0, 0);
      ctx.restore();
    }

    const anyProgress = progressPerBar(n-1) > 0.3;
    if(anyProgress){
      const ye = yPix(E);
      ctx.setLineDash([8,6]);
      ctx.strokeStyle = '#c96f6f';
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(padL, ye); ctx.lineTo(W-padR, ye); ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = '20px "JetBrains Mono", monospace';
      ctx.fillStyle = '#c96f6f';
      ctx.textAlign = 'left';
      ctx.fillText('e = ' + E.toFixed(6), W - padR - 210, ye - 10);
    }
  }

  function animEx1(){
    const cv = document.getElementById('c1');
    const cap = document.getElementById('c1cap');
    const val = document.getElementById('c1val');
    const n = ex1.labels.length;
    const perBarMs = 260;
    const start = performance.now();
    function frame(t){
      const elapsed = t - start;
      const progressPerBar = (i) => (elapsed - i*perBarMs*0.75) / perBarMs;
      drawEx1(cv, progressPerBar);

      const activeIdx = Math.min(n-1, Math.floor(elapsed / (perBarMs*0.75)));
      cap.textContent = "n = " + ex1.labels[activeIdx];
      val.textContent = "(1 + 1/n)ⁿ ≈ " + ex1.values[activeIdx].toFixed(6);

      if(elapsed < (n-1)*perBarMs*0.75 + perBarMs + 400){
        requestAnimationFrame(frame);
      } else {
        cap.textContent = "settled at n = " + ex1.labels[n-1];
        val.textContent = "≈ e";
      }
    }
    requestAnimationFrame(frame);
  }

  function drawEx2(cv, hIndexFloat){
    const ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    ctx.clearRect(0,0,W,H);

    const padL = 70, padR = 30, padT = 30, padB = 90;
    const plotW = W - padL - padR, plotH = H - padT - padB;
    const yMin = 0.6, yMax = 1.25;
    function yPix(v){ return padT + plotH * (1 - (v - yMin)/(yMax - yMin)); }

    ctx.strokeStyle = 'rgba(234,227,211,0.08)';
    ctx.lineWidth = 1;
    ctx.font = '20px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(234,227,211,0.45)';
    for(let v = 0.6; v <= 1.25; v += 0.1){
      const y = yPix(v);
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
      ctx.fillText(v.toFixed(2), 10, y+6);
    }

    const n = ex2.hLabels.length;
    const groupGap = 26;
    const groupW = (plotW - groupGap*(n-1)) / n;
    const barW = groupW * 0.27;
    const colors = { a2:'#6fa6c9', ae:'#d9a441', a3:'#c96f6f' };
    const limits = { a2: ex2.lim2, ae: ex2.lime, a3: ex2.lim3 };

    const idx = Math.min(n-1, Math.max(0, hIndexFloat));
    const fullIdx = Math.floor(idx);
    const frac = idx - fullIdx;

    function valAt(arr, i, f){
      if(i >= arr.length-1) return arr[arr.length-1];
      return arr[i] + (arr[i+1]-arr[i]) * ease(f);
    }

    for(let i=0;i<n;i++){
      const gx = padL + i*(groupW+groupGap);
      if(i > fullIdx) continue;
      const f = (i===fullIdx) ? frac : 1;

      ['a2','ae','a3'].forEach((key, k) => {
        const series = ex2[key];
        const v = i < fullIdx ? series[i] : valAt(series, i, f);
        const x = gx + k*(barW+6);
        const yTop = yPix(v);
        const yBase = yPix(yMin);
        ctx.fillStyle = colors[key];
        ctx.globalAlpha = 0.9;
        ctx.fillRect(x, yTop, barW, yBase - yTop);
        ctx.globalAlpha = 1;
      });

      ctx.save();
      ctx.font = '18px "JetBrains Mono", monospace';
      ctx.fillStyle = 'rgba(234,227,211,0.6)';
      ctx.textAlign = 'center';
      ctx.fillText(ex2.hLabels[i], gx + groupW/2, H - padB + 34);
      ctx.restore();
    }

    ['a2','ae','a3'].forEach(key=>{
      const y = yPix(limits[key]);
      ctx.setLineDash([7,5]);
      ctx.strokeStyle = colors[key];
      ctx.globalAlpha = 0.6;
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W-padR, y); ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
    });
  }

  function animEx2(){
    const cv = document.getElementById('c2');
    const cap = document.getElementById('c2cap');
    const val = document.getElementById('c2val');
    const n = ex2.hLabels.length;
    const perStepMs = 620;
    const start = performance.now();
    function frame(t){
      const elapsed = t - start;
      const hIndexFloat = elapsed / perStepMs;
      drawEx2(cv, hIndexFloat);
      const shown = Math.min(n-1, Math.floor(hIndexFloat));
      cap.textContent = ex2.hLabels[shown];
      val.textContent = "→ ln2=" + ex2.a2[shown].toFixed(4) + "  ln e=" + ex2.ae[shown].toFixed(4) + "  ln3=" + ex2.a3[shown].toFixed(4);
      if(hIndexFloat < n){
        requestAnimationFrame(frame);
      } else {
        drawEx2(cv, n-1);
        cap.textContent = "settled";
        val.textContent = "ln2=" + ex2.lim2.toFixed(4) + "   ln e=" + ex2.lime.toFixed(4) + "   ln3=" + ex2.lim3.toFixed(4);
      }
    }
    requestAnimationFrame(frame);
  }

  function bandColor(d){
    if(d < 2) return '#c96f6f';
    if(d < 6) return '#d9a441';
    if(d < 14) return '#7fb08a';
    return '#6fa6c9';
  }

  function drawEx3(cv, pointsShown, partial){
    const ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    ctx.clearRect(0,0,W,H);

    const padL = 90, padR = 40, padT = 30, padB = 70;
    const plotW = W - padL - padR, plotH = H - padT - padB;

    const xMin = Math.log10(1), xMax = Math.log10(10000);
    const yMin = Math.log10(1e-16), yMax = Math.log10(1);

    function xPix(N){ return padL + plotW * (Math.log10(N) - xMin)/(xMax-xMin); }
    function yPix(e){ return padT + plotH * (1 - (Math.log10(e) - yMin)/(yMax-yMin)); }

    ctx.strokeStyle = 'rgba(234,227,211,0.08)';
    ctx.font = '18px "JetBrains Mono", monospace';
    ctx.fillStyle = 'rgba(234,227,211,0.45)';
    for(let e=-16; e<=0; e+=2){
      const y = padT + plotH*(1 - (e - yMin)/(yMax-yMin));
      ctx.beginPath(); ctx.moveTo(padL,y); ctx.lineTo(W-padR,y); ctx.stroke();
      ctx.fillText('1e' + e, 12, y+6);
    }
    [1,10,100,1000,10000].forEach(N=>{
      const x = xPix(N);
      ctx.beginPath(); ctx.moveTo(x,padT); ctx.lineTo(x,H-padB); ctx.stroke();
      ctx.fillText('N=' + N, x-20, H-padB+26);
    });

    const yb1 = yPix(3e-16), yb2 = yPix(1e-16);
    ctx.fillStyle = 'rgba(111,166,201,0.12)';
    ctx.fillRect(padL, yb1, plotW, yb2-yb1);
    ctx.fillStyle = 'rgba(111,166,201,0.75)';
    ctx.font = '16px "JetBrains Mono", monospace';
    ctx.fillText('machine precision floor (~1e-16)', padL+10, yb2-8);

    ctx.beginPath();
    ctx.strokeStyle = 'rgba(234,227,211,0.35)';
    ctx.lineWidth = 1.5;
    for(let i=0;i<pointsShown;i++){
      const x = xPix(ex3.N[i]);
      const y = yPix(Math.max(ex3.err[i], 1e-16));
      if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    if(partial > 0 && pointsShown < ex3.N.length){
      const i = pointsShown;
      const x0 = xPix(ex3.N[i-1]), y0 = yPix(Math.max(ex3.err[i-1],1e-16));
      const x1 = xPix(ex3.N[i]), y1 = yPix(Math.max(ex3.err[i],1e-16));
      ctx.lineTo(x0 + (x1-x0)*partial, y0 + (y1-y0)*partial);
    }
    ctx.stroke();

    for(let i=0;i<pointsShown;i++){
      const x = xPix(ex3.N[i]);
      const y = yPix(Math.max(ex3.err[i], 1e-16));
      const c = bandColor(ex3.digits[i]);
      ctx.beginPath();
      ctx.arc(x,y, 7, 0, Math.PI*2);
      ctx.fillStyle = c;
      ctx.fill();
      ctx.strokeStyle = 'rgba(22,38,31,0.8)';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = '16px "JetBrains Mono", monospace';
      ctx.fillStyle = c;
      ctx.textAlign = 'center';
      ctx.fillText(ex3.digits[i].toFixed(1) + 'd', x, y-16);
      ctx.textAlign = 'left';
    }
  }

  function animEx3(){
    const cv = document.getElementById('c3');
    const cap = document.getElementById('c3cap');
    const val = document.getElementById('c3val');
    const n = ex3.N.length;
    const perPointMs = 420;
    const start = performance.now();
    function frame(t){
      const elapsed = t - start;
      const raw = elapsed / perPointMs;
      const pointsShown = Math.min(n, Math.floor(raw)+1);
      const partial = raw - Math.floor(raw);
      drawEx3(cv, Math.min(pointsShown, n), partial);

      const shown = Math.min(n, pointsShown) - 1;
      cap.textContent = "N = " + ex3.N[shown];
      val.textContent = "error ≈ " + ex3.err[shown].toExponential(2) + "  (" + ex3.digits[shown].toFixed(1) + " correct digits)";

      if(raw < n){
        requestAnimationFrame(frame);
      } else {
        drawEx3(cv, n, 0);
        cap.textContent = "N = " + ex3.N[n-1];
        val.textContent = "flat at machine precision — ~" + ex3.digits[n-1].toFixed(1) + " correct digits";
      }
    }
    requestAnimationFrame(frame);
  }

  onEnter(document.getElementById('c1'), animEx1);
  onEnter(document.getElementById('c2'), animEx2);
  onEnter(document.getElementById('c3'), animEx3);

})();
</script>
</body>
</html>
"""

e_digits_str = f"{E_CONST:.16f}".split(".")[1]  # digits after "2."

html_out = (
    HTML_TEMPLATE
    .replace("__E_DIGITS__", e_digits_str)
    .replace("__EX1_JSON__", json.dumps(ex1_data))
    .replace("__EX2_JSON__", json.dumps(ex2_data))
    .replace("__EX3_JSON__", json.dumps(ex3_data))
    .replace("__E_CONST__", repr(E_CONST))
)

report_path = Path("./e_report.html").resolve()
report_path.write_text(html_out, encoding="utf-8")
print(f"Saved -> {report_path}")

webbrowser.open(report_path.as_uri())
