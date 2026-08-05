#!/usr/bin/env python3
"""Generate original vector diagrams for the Polar coordinates lesson."""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper-1" / "figures" / "polar"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#2563eb"
CORAL = "#e85d75"
GREEN = "#059669"
PURPLE = "#7c3aed"
INK = "#172033"
MUTED = "#64748b"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Plot:
    def __init__(self, title: str, limit: float = 5.0, width: int = 720, height: int = 480):
        self.title = title
        self.limit = limit
        self.w = width
        self.h = height
        self.cx = width / 2
        self.cy = height / 2 + 12
        self.scale = min(width - 110, height - 90) / (2 * limit)
        self.items: list[str] = []

    def xy(self, x: float, y: float) -> tuple[float, float]:
        return self.cx + x * self.scale, self.cy - y * self.scale

    def axes(self, ticks: tuple[float, ...] = ()) -> "Plot":
        left, right = self.xy(-self.limit, 0)[0], self.xy(self.limit, 0)[0]
        top, bottom = self.xy(0, self.limit)[1], self.xy(0, -self.limit)[1]
        self.items.append(f'<path class="axis" marker-end="url(#arrow)" d="M{left:.1f},{self.cy:.1f}H{right+8:.1f}"/>')
        self.items.append(f'<path class="axis" marker-end="url(#arrow)" d="M{self.cx:.1f},{bottom:.1f}V{top-8:.1f}"/>')
        self.items.append(f'<text class="axis-label" x="{right+14:.1f}" y="{self.cy+5:.1f}">initial line</text>')
        self.items.append(f'<text class="axis-label" x="{self.cx+8:.1f}" y="{top-10:.1f}">y</text>')
        self.items.append(f'<text class="tick-label" x="{self.cx-17:.1f}" y="{self.cy+18:.1f}">O</text>')
        for t in ticks:
            for sign in (-1, 1):
                x, y = self.xy(sign * t, 0)
                self.items.append(f'<path class="tick" d="M{x:.1f},{y-4:.1f}v8"/>')
                self.items.append(f'<text class="tick-label" x="{x:.1f}" y="{y+19:.1f}" text-anchor="middle">{esc(sign*t)}</text>')
        return self

    def _path(self, points: list[tuple[float, float]], color: str, width: float = 3.2,
              fill: str = "none", opacity: float = 1.0, dash: str = "") -> None:
        if len(points) < 2:
            return
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in points)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(
            f'<path class="curve" d="{d}" stroke="{color}" stroke-width="{width}" '
            f'fill="{fill}" opacity="{opacity}"{dash_attr}/>'
        )

    def polar(self, fn, start: float, end: float, color: str = BLUE, samples: int = 900,
              label: str | None = None, width: float = 3.2) -> "Plot":
        points: list[tuple[float, float]] = []
        for i in range(samples + 1):
            theta = start + (end - start) * i / samples
            try:
                r = fn(theta)
            except (ValueError, ZeroDivisionError, OverflowError):
                r = float("nan")
            if math.isfinite(r) and r >= -1e-9 and abs(r) <= self.limit * 2:
                x, y = r * math.cos(theta), r * math.sin(theta)
                points.append(self.xy(x, y))
            else:
                self._path(points, color, width)
                points = []
        self._path(points, color, width)
        if label:
            y = 48 + 22 * sum('class="legend"' in item for item in self.items)
            self.items.append(
                f'<g class="legend"><path stroke="{color}" stroke-width="3" d="M{self.w-230},{y}h28"/>'
                f'<text x="{self.w-194}" y="{y+5}">{esc(label)}</text></g>'
            )
        return self

    def cartesian(self, fn, start: float, end: float, color: str = BLUE, samples: int = 600,
                  label: str | None = None) -> "Plot":
        points = []
        for i in range(samples + 1):
            x = start + (end - start) * i / samples
            try:
                y = fn(x)
            except (ValueError, ZeroDivisionError):
                y = float("nan")
            if math.isfinite(y) and abs(y) <= self.limit * 1.2:
                points.append(self.xy(x, y))
            else:
                self._path(points, color)
                points = []
        self._path(points, color)
        if label:
            self.legend(label, color)
        return self

    def circle(self, radius: float, color: str = BLUE, label: str | None = None) -> "Plot":
        return self.polar(lambda _t: radius, 0, 2 * math.pi, color, label=label)

    def ray(self, theta: float, radius: float | None = None, color: str = CORAL,
            label: str | None = None, dash: bool = False) -> "Plot":
        radius = radius or self.limit
        p0, p1 = self.xy(0, 0), self.xy(radius * math.cos(theta), radius * math.sin(theta))
        self._path([p0, p1], color, 2.2, dash="7 6" if dash else "")
        if label:
            self.items.append(f'<text class="point-label" x="{p1[0]-8:.1f}" y="{p1[1]-8:.1f}" text-anchor="end">{esc(label)}</text>')
        return self

    def point(self, r: float, theta: float, label: str, color: str = INK, dx: float = 8, dy: float = -9) -> "Plot":
        x, y = self.xy(r * math.cos(theta), r * math.sin(theta))
        self.items.append(f'<circle class="point" cx="{x:.1f}" cy="{y:.1f}" r="4.3" fill="{color}"/>')
        self.items.append(f'<text class="point-label" x="{x+dx:.1f}" y="{y+dy:.1f}">{esc(label)}</text>')
        return self

    def legend(self, label: str, color: str) -> "Plot":
        count = sum('class="legend"' in item for item in self.items)
        y = 48 + 22 * count
        self.items.append(
            f'<g class="legend"><path stroke="{color}" stroke-width="3" d="M{self.w-230},{y}h28"/>'
            f'<text x="{self.w-194}" y="{y+5}">{esc(label)}</text></g>'
        )
        return self

    def save(self, name: str, caption: str) -> None:
        svg = f'''<figure class="math-figure"><svg class="math-plot" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="{name}-title {name}-desc" xmlns="http://www.w3.org/2000/svg">
<title id="{name}-title">{esc(self.title)}</title><desc id="{name}-desc">{esc(caption)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="{INK}"/></marker><clipPath id="clip"><rect x="18" y="35" width="{self.w-36}" height="{self.h-52}"/></clipPath></defs>
<rect class="plot-bg" x="1" y="1" width="{self.w-2}" height="{self.h-2}" rx="14"/>
<text class="plot-title" x="{self.w/2}" y="27" text-anchor="middle">{esc(self.title)}</text>
<g clip-path="url(#clip)">{''.join(self.items)}</g></svg><figcaption>{esc(caption)}</figcaption></figure>'''
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def examples() -> None:
    p = Plot("Example 5.1: points in polar and Cartesian form", 14).axes()
    for r, t, label, color in [
        (4, 2 * math.pi / 3, "(4, 2π/3)", BLUE),
        (12, -math.pi / 6, "(12, −π/6)", CORAL),
        (2, 5 * math.pi / 6, "(−√3, 1)", GREEN),
        (4 * math.sqrt(2), -math.pi / 4, "(4, −4)", PURPLE),
    ]:
        p.ray(t, r, color=color).point(r, t, label, color=color)
    p.save("example-5-1", "Each point is located by a radius from the pole and an angle from the initial line.")

    p = Plot("Example 5.2: Cartesian curves before conversion", 8).axes()
    p.cartesian(lambda x: math.sqrt(x*x-9), 3, 8, BLUE).cartesian(lambda x: -math.sqrt(x*x-9), 3, 8, BLUE)
    p.cartesian(lambda x: math.sqrt(x*x-9), -8, -3, BLUE).cartesian(lambda x: -math.sqrt(x*x-9), -8, -3, BLUE)
    p.cartesian(lambda x: x + 4, -8, 4, CORAL).legend("x² − y² = 9", BLUE).legend("y = x + 4", CORAL)
    p.save("example-5-2", "The same geometric curves can be described by polar equations.")

    p = Plot("Example 5.3: r = 5 and r² = 4 sin θ", 5.8).axes(ticks=(5,))
    p.circle(5, BLUE, "r = 5").polar(lambda t: math.sqrt(max(0, 4 * math.sin(t))), 0, math.pi, CORAL, label="r² = 4 sin θ")
    p.save("example-5-3", "The plotted polar curves correspond to the derived Cartesian equations.")

    p = Plot("Example 5.4: a constant radius and a constant angle", 4).axes(ticks=(3,))
    p.circle(3, BLUE, "r = 3").ray(math.pi / 4, 4, CORAL, "θ = π/4")
    p.point(3, 0, "(3, 0)")
    p.save("example-5-4", "A constant r gives a circle; a constant θ gives a half-line.")

    p = Plot("Example 5.5: r = 5 cos² θ", 5.8).axes(ticks=(5,))
    p.polar(lambda t: 5 * math.cos(t) ** 2, 0, 2 * math.pi, BLUE)
    p.point(5, 0, "r = 5").point(5, math.pi, "r = 5", dx=-55)
    p.save("example-5-5", "The curve is symmetric about both coordinate axes and reaches the pole when cos θ = 0.")

    p = Plot("Example 5.6: r = 3 + 2 cos 4θ", 5.8).axes(ticks=(1, 5))
    p.polar(lambda t: 3 + 2 * math.cos(4 * t), 0, 2 * math.pi, BLUE)
    p.save("example-5-6", "Fourfold rotational symmetry; 1 ≤ r ≤ 5.")

    p = Plot("Example 5.7: r = θ(π − θ), r ≥ 0", 3.2).axes()
    p.polar(lambda t: t * (math.pi - t), 0, math.pi, BLUE)
    p.ray(math.pi / 2, math.pi**2 / 4, MUTED, "r = π²/4", dash=True)
    p.save("example-5-7", "Only the interval 0 ≤ θ ≤ π is drawn because the stated course convention excludes negative r.")

    p = Plot("Example 5.8: r = 1 + 2 cos θ", 3.5).axes(ticks=(1, 3))
    p.polar(lambda t: 1 + 2 * math.cos(t), -2 * math.pi / 3, 2 * math.pi / 3, BLUE)
    p.ray(2 * math.pi / 3, 2.6, MUTED, "θ = 2π/3", dash=True).ray(-2 * math.pi / 3, 2.6, MUTED, "θ = −2π/3", dash=True)
    p.point(3, 0, "(3, 0)")
    p.save("example-5-8", "The curve reaches the pole at θ = ±2π/3 and is symmetric about the initial line.")


def textbook_exercises() -> None:
    p = Plot("Exercise 5B Q9: two polar curves", 1.25).axes()
    p.circle(.5, BLUE, "C₁: r = 1/2").polar(lambda t: math.sin(t / 2), 0, math.pi, CORAL, label="C₂: r = sin(θ/2)")
    p.point(.5, math.pi / 3, "(1/2, π/3)")
    p.save("exercise-5b-9", "The circle and C₂ meet at θ = π/3.")

    p = Plot("Exercise 5C Q9: r = a(1 + sin θ)", 2.4).axes()
    p.polar(lambda t: 1 + math.sin(t), 0, 2 * math.pi, BLUE)
    p.ray(math.pi / 3, 2.2, CORAL, "θ = π/3", dash=True).ray(2 * math.pi / 3, 2.2, CORAL, "θ = 2π/3", dash=True)
    p.point(2, math.pi / 2, "r = 2a")
    p.save("exercise-5c-9", "The required sector lies between the two coral half-lines; the drawing is scaled with a = 1.")

    p = Plot("Exercise 5C Q10: r = 2 + 2 cos θ", 4.5).axes(ticks=(4,))
    p.polar(lambda t: 2 + 2 * math.cos(t), 0, math.pi, BLUE)
    p.ray(math.pi / 5, 4.2, CORAL, "θ = π/5", dash=True)
    p.point(4, 0, "(4, 0)")
    p.save("exercise-5c-10", "The half-line θ = π/5 divides the upper half-cardioid into the two required regions.")


def past_papers() -> None:
    def single(name, title, fn, start, end, limit, caption, rays=(), points=()):
        p = Plot(title, limit).axes()
        p.polar(fn, start, end, BLUE)
        for theta, label in rays:
            p.ray(theta, limit * .92, CORAL, label, dash=True)
        for radius, theta, label in points:
            p.point(radius, theta, label)
        p.save(name, caption)

    p = Plot("2019 M/J 11–12: C₁ and C₂", 2.0).axes()
    p.polar(lambda t: math.sqrt(2*t), 0, math.pi/2, BLUE, label="C₁")
    p.polar(lambda t: math.sqrt(t)/math.cos(t), 0, math.pi/2-.03, CORAL, label="C₂")
    p.point(math.sqrt(math.pi/2), math.pi/4, "Q").save("past-2019-mj-11-12", "The curves meet at θ = π/4; the shaded-area calculation uses 0 ≤ θ ≤ π/4.")

    single("past-2019-mj-13", "2019 M/J 13: r² = ln(1 + θ)", lambda t: math.sqrt(math.log1p(t)), 0, 2*math.pi, 1.6, "An increasing anticlockwise spiral, tangent to the initial line at the pole.")

    a = math.log(1+math.sqrt(2))
    p = Plot("2019 O/N: exponential polar curves", 6.5).axes()
    p.polar(lambda t: 2*(math.exp(t)+math.exp(-t)), 0, a, BLUE, label="C₁")
    p.polar(lambda t: math.exp(2*t)-math.exp(-2*t), 0, a, CORAL, label="C₂")
    p.point(4*math.sqrt(2), a, "P").save("past-2019-on", "The curves and the initial line enclose the required region before P.")

    p = Plot("2020 M/J 11–12: C₁ and C₂", 1.1).axes()
    p.polar(lambda t: t*math.cos(t), 0, math.pi/2, BLUE, label="C₁")
    p.polar(lambda t: t*math.sin(t), 0, math.pi/2, CORAL, label="C₂")
    p.point(math.pi/(4*math.sqrt(2)), math.pi/4, "Q").save("past-2020-mj-11-12", "The curves meet away from the pole at θ = π/4.")

    single("past-2020-mj-13", "2020 M/J 13: r = a tan θ", math.tan, 0, math.pi/4, 1.25, "Scaled with a = 1; the greatest radius is a.", rays=((math.pi/4,"θ = π/4"),))
    single("past-2020-on-11-13", "2020 O/N 11–13: r = sin 4θ", lambda t: math.sin(4*t), 0, math.pi/4, 1.2, "A single loop symmetric about θ = π/8.", rays=((math.pi/8,"θ = π/8"),))
    single("past-2020-on-12", "2020 O/N 12: r = ln(1 + π − θ)", lambda t: math.log(1+math.pi-t), 0, math.pi, 1.65, "The radius decreases from ln(1 + π) to zero.")

    single("past-2021-mj-11-12", "2021 M/J 11–12: r = 2 cot(π/3 − θ)", lambda t: 2/math.tan(math.pi/3-t), 0, math.pi/6, 3.8, "The radius increases to 2√3.", rays=((math.pi/6,"θ = π/6"),))
    single("past-2021-mj-13", "2021 M/J 13: reciprocal-difference curve", lambda t: 1/(math.pi-t)-1/math.pi, 0, math.pi/2, .38, "The curve leaves the pole tangentially and has increasing radius.")
    single("past-2021-on-11-13", "2021 O/N 11–13", lambda t: 2*math.cos(t)*(1+math.sin(t)), 0, math.pi/2, 2.9, "The maximum radius occurs at θ = π/6.", points=((3*math.sqrt(3)/2,math.pi/6,"maximum"),))
    p = Plot("2021 O/N 12: curve and y = 2", 5.5).axes()
    p.polar(lambda t: 3+2*math.sin(t), -math.pi, math.pi, BLUE, label="C")
    x1,y1=p.xy(-5.2,2); x2,y2=p.xy(5.2,2); p._path([(x1,y1),(x2,y2)],CORAL,2.3)
    p.point(4,math.pi/6,"(4, π/6)").point(4,5*math.pi/6,"(4, 5π/6)",dx=-76)
    p.save("past-2021-on-12", "The horizontal line y = 2 cuts the symmetric closed curve at two points.")

    single("past-2022-mj-11-12", "2022 M/J 11–12", lambda t: math.sqrt(math.atan(t/2)), 0, 2, 1.05, "The radius increases to √π/2.", rays=((2,"θ = 2"),))
    single("past-2022-mj-13", "2022 M/J 13", lambda t: math.sqrt(2/(2+math.sin(2*t))), 0, math.pi/4, 1.25, "Scaled with a = 1; the radius decreases on 0 ≤ θ ≤ π/4.", rays=((math.pi/4,"θ = π/4"),))

    p = Plot("2023 O/N 11–13: C₁ and C₂", 1.2).axes()
    p.polar(math.cos, 0, math.pi/2, BLUE, label="C₁")
    p.polar(lambda t: math.sin(2*t), 0, math.pi/2, CORAL, label="C₂")
    p.point(math.sqrt(3)/2,math.pi/6,"P").save("past-2023-on-11-13", "The required region is bounded by different curves on either side of P.")
    single("past-2023-on-12", "2023 O/N 12", lambda t: math.exp(-t)-math.exp(-math.pi/2), 0, math.pi/2, .9, "The radius decreases from 1 − e^(−π/2) to the pole.")

    single("past-2024-mj-11-12", "2024 M/J 11–12", lambda t: math.sqrt((math.pi-t)*math.atan(math.pi-t)), 0, math.pi, 2.2, "A decreasing-radius arc from the initial line to the pole.")
    single("past-2024-mj-13", "2024 M/J 13", lambda t: math.sqrt(max(0,math.sin(2*t)*math.cos(t))), 0, math.pi, 1.15, "Two loops symmetric about θ = π/2.", rays=((math.pi/2,"θ = π/2"),))
    single("past-2024-on-11-13", "2024 O/N 11–13", lambda t: math.sqrt(max(0,3*math.sin(2*t))), 0, math.pi/2, 1.9, "A loop symmetric about θ = π/4 with maximum radius √3.", rays=((math.pi/4,"θ = π/4"),))
    phi=1.2587
    p = Plot("2024 O/N 12: circle and spiral", 1.65).axes()
    p.polar(lambda t: math.cos(t)+math.sin(t), -math.pi/4, 3*math.pi/4, BLUE, label="C₁")
    p.polar(lambda t: t, 0, phi, CORAL, label="C₂")
    p.point(phi,phi,"P").save("past-2024-on-12", "Scaled with a = 1; the circle and spiral meet at φ ≈ 1.259.")

    single("past-2025-mj-11-12", "2025 M/J 11–12", lambda t: t*math.exp(t/8), 0, 2*math.pi, 14.5, "An outward anticlockwise spiral from θ = 0 to 2π.")
    single("past-2025-mj-13", "2025 M/J 13", lambda t: math.sqrt(max(0,math.exp(math.sin(t))*math.cos(t))), -math.pi/2, math.pi/2, 1.35, "The two marked extrema are found by maximising r and r cos θ.", points=((1.208,.666,"max r"),(1.136,.308,"max x")))
    single("past-2025-mj-14", "2025 M/J 14", lambda t: math.tan(t/8), 0, 2*math.pi, 1.25, "Scaled with a = 1; the spiral reaches r = a at θ = 2π.")
    single("past-2025-on-11-13", "2025 O/N 11–13", lambda t: math.sin(3*t), 0, math.pi/3, 1.2, "A single loop symmetric about θ = π/6.", rays=((math.pi/6,"θ = π/6"),))
    single("past-2025-on-12", "2025 O/N 12", lambda t: math.sqrt(math.tan(2*t)), 0, math.pi/8, 1.2, "The radius increases from zero to one.", rays=((math.pi/8,"θ = π/8"),))
    single("past-2025-on-14", "2025 O/N 14", lambda t: math.cos(t/2), 0, math.pi, 1.2, "A single arc from (1, 0) to the pole through the upper half-plane.")


if __name__ == "__main__":
    examples()
    textbook_exercises()
    past_papers()
    print(f"Generated {len(list(OUT.glob('*.svg')))} SVG fragments in {OUT}")
