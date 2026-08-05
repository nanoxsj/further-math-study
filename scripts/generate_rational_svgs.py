#!/usr/bin/env python3
"""Generate original, textbook-style inline SVG diagrams for Chapter 1.2.

The output contains no scripts or external assets: Quarto includes each SVG
verbatim in the final HTML, so the published lesson works fully offline.
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper-1" / "figures" / "rational"
OUT.mkdir(parents=True, exist_ok=True)

BLUE, CORAL, GREEN = "#2563eb", "#e85d75", "#059669"
INK, MUTED, GRID = "#172033", "#64748b", "#d7deea"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Plot:
    def __init__(self, title, xlim=(-5, 5), ylim=(-5, 5), width=720, height=420):
        self.title, self.xlim, self.ylim = title, xlim, ylim
        self.w, self.h, self.m = width, height, 52
        self.items = []

    def X(self, x): return self.m + (x-self.xlim[0])/(self.xlim[1]-self.xlim[0])*(self.w-2*self.m)
    def Y(self, y): return self.h-self.m - (y-self.ylim[0])/(self.ylim[1]-self.ylim[0])*(self.h-2*self.m)

    def axes(self, xticks=None, yticks=None, xlabel="x", ylabel="y"):
        xticks = xticks if xticks is not None else range(math.ceil(self.xlim[0]), math.floor(self.xlim[1])+1)
        yticks = yticks if yticks is not None else range(math.ceil(self.ylim[0]), math.floor(self.ylim[1])+1)
        x0 = self.Y(0) if self.ylim[0] <= 0 <= self.ylim[1] else self.Y(self.ylim[0])
        y0 = self.X(0) if self.xlim[0] <= 0 <= self.xlim[1] else self.X(self.xlim[0])
        for x in xticks:
            if self.xlim[0] <= x <= self.xlim[1]:
                X=self.X(x); self.items.append(f'<path class="tick" d="M{X:.1f},{x0-4:.1f}v8"/>')
                if x: self.items.append(f'<text class="tick-label" x="{X:.1f}" y="{x0+19:.1f}" text-anchor="middle">{esc(x)}</text>')
        for y in yticks:
            if self.ylim[0] <= y <= self.ylim[1]:
                Y=self.Y(y); self.items.append(f'<path class="tick" d="M{y0-4:.1f},{Y:.1f}h8"/>')
                if y: self.items.append(f'<text class="tick-label" x="{y0-9:.1f}" y="{Y+4:.1f}" text-anchor="end">{esc(y)}</text>')
        self.items += [f'<path class="axis" marker-end="url(#arrow)" d="M{self.m},{x0}H{self.w-self.m+5}"/>',
                       f'<path class="axis" marker-end="url(#arrow)" d="M{y0},{self.h-self.m}V{self.m-5}"/>',
                       f'<text class="axis-label" x="{self.w-self.m+12}" y="{x0+5}">{xlabel}</text>',
                       f'<text class="axis-label" x="{y0+8}" y="{self.m-9}">{ylabel}</text>']
        return self

    def asym_v(self, x, label=None):
        X=self.X(x); self.items.append(f'<path class="asym" d="M{X},{self.m}V{self.h-self.m}"/>')
        if label: self.items.append(f'<text class="asym-label" x="{X+6}" y="{self.m+15}">{esc(label)}</text>')
        return self

    def asym_h(self, y, label=None):
        Y=self.Y(y); self.items.append(f'<path class="asym" d="M{self.m},{Y}H{self.w-self.m}"/>')
        if label: self.items.append(f'<text class="asym-label" x="{self.w-self.m-5}" y="{Y-7}" text-anchor="end">{esc(label)}</text>')
        return self

    def asym_line(self, f, label=None):
        x1,x2=self.xlim; y1,y2=f(x1),f(x2)
        self.items.append(f'<path class="asym" d="M{self.X(x1)},{self.Y(y1)}L{self.X(x2)},{self.Y(y2)}"/>')
        if label: self.items.append(f'<text class="asym-label" x="{self.X(x2)-8}" y="{self.Y(y2)-8}" text-anchor="end">{esc(label)}</text>')
        return self

    def curve(self, f, color=BLUE, intervals=None, label=None, samples=700, width=3):
        intervals = intervals or [self.xlim]
        for a,b in intervals:
            pts=[]
            for i in range(samples+1):
                x=a+(b-a)*i/samples
                try: y=f(x)
                except (ValueError, ZeroDivisionError, OverflowError): y=float("nan")
                if math.isfinite(y) and self.ylim[0]-.8 <= y <= self.ylim[1]+.8:
                    pts.append((self.X(x),self.Y(y)))
                else:
                    if len(pts)>1: self._path(pts,color,width)
                    pts=[]
            if len(pts)>1: self._path(pts,color,width)
        if label:
            self.items.append(f'<g class="legend"><path stroke="{color}" stroke-width="{width}" d="M{self.w-190},28h28"/><text x="{self.w-154}" y="33">{esc(label)}</text></g>')
        return self

    def _path(self, pts, color, width):
        d="M"+" L".join(f"{x:.1f},{y:.1f}" for x,y in pts)
        self.items.append(f'<path class="curve" stroke="{color}" stroke-width="{width}" d="{d}"/>')

    def point(self,x,y,label,dx=9,dy=-10,open_=False,color=INK):
        cls="point open" if open_ else "point"
        self.items.append(f'<circle class="{cls}" stroke="{color}" cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="4.5"/>')
        self.items.append(f'<text class="point-label" x="{self.X(x)+dx:.1f}" y="{self.Y(y)+dy:.1f}">{esc(label)}</text>')
        return self

    def save(self, name, caption):
        svg=f'''<figure class="math-figure"><svg class="math-plot" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="{name}-title {name}-desc" xmlns="http://www.w3.org/2000/svg">
<title id="{name}-title">{esc(self.title)}</title><desc id="{name}-desc">{esc(caption)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="{INK}"/></marker><clipPath id="clip"><rect x="{self.m}" y="{self.m}" width="{self.w-2*self.m}" height="{self.h-2*self.m}"/></clipPath></defs>
<rect class="plot-bg" x="1" y="1" width="{self.w-2}" height="{self.h-2}" rx="14"/>
<text class="plot-title" x="{self.w/2}" y="29" text-anchor="middle">{esc(self.title)}</text>
<g clip-path="url(#clip)">{''.join(self.items)}</g></svg><figcaption>{esc(caption)}</figcaption></figure>'''
        (OUT/f"{name}.svg").write_text(svg,encoding="utf-8")


def base(title,xlim=(-5,5),ylim=(-5,5),ticks=True):
    p=Plot(title,xlim,ylim); return p.axes() if ticks else p


def examples():
    p=base("Example 4.1: y = (x² + 1)/(x² + 2)",(-5,5),(0,1.35),yticks:=True)
    p.asym_h(1,"y = 1").curve(lambda x:(x*x+1)/(x*x+2)).point(0,.5,"(0, ½)").save("example-4-1","A minimum at (0, 1/2) and horizontal asymptote y = 1.")

    # A qualitative cubic matching all stated stationary-point coordinates.
    f=lambda x: -15/32*x**3+45/32*x*x+135/32*x-245/32
    p=base("Example 4.2: given curve y = f(x)",(-5,5),(-12,8)); p.curve(f,CORAL).point(-1,-10,"P(−1, −10)").point(3,5,"Q(3, 5)").save("example-4-2-given","The given curve, redrawn from its stated stationary points.")
    p=base("Example 4.2: transformations",(-5,5),(-12,12)); p.curve(f,MUTED,label="y = f(x)").curve(lambda x:abs(f(x)),BLUE,label="y = |f(x)|").point(-1,10,"(-1, 10)").point(3,5,"(3, 5)").save("example-4-2a","Negative portions are reflected in the x-axis.")
    p=base("Example 4.2: y = f(|x|)",(-5,5),(-4,12)); p.curve(lambda x:f(abs(x)),GREEN).point(-3,5,"(-3, 5)").point(3,5,"(3, 5)").save("example-4-2b","The right-hand half is reflected in the y-axis.")

    p=base("Example 4.3: reciprocal trigonometric curves",(-360,360),(-4,4));
    for a in (-270,-90,90,270): p.asym_v(a)
    ints=[(-360,-270.5),(-269.5,-90.5),(-89.5,89.5),(90.5,269.5),(270.5,360)]
    p.curve(lambda x:1/math.cos(math.radians(x)),BLUE,ints,label="y = sec x",samples=350)
    p.save("example-4-3a","The secant curve has vertical asymptotes where cos x = 0.")
    p=base("Example 4.3: y = cot x",(-360,360),(-4,4));
    for a in (-360,-180,0,180,360): p.asym_v(a)
    ints=[(-359.5,-180.5),(-179.5,-.5),(.5,179.5),(180.5,359.5)]
    p.curve(lambda x:1/math.tan(math.radians(x)),CORAL,ints)
    for x in (-270,-90,90,270): p.point(x,0,"",open_=True,color=CORAL)
    p.save("example-4-3b","Open points record where the stated tan function is undefined.")

    # f=(4-2x)/(1-x) has exactly the given asymptotes and intercepts.
    f=lambda x:(4-2*x)/(1-x)
    rational_plot("example-4-4-given","Example 4.4: given curve y = f(x)",f,(-4,6),(-4,5),[(1,"x = 1")],[(2,"y = 2")],points=[(0,4,"(0, 4)"),(2,0,"(2, 0)")],caption="The given curve, reconstructed exactly from its asymptotes and intercepts.")
    p=base("Example 4.4: f and its reciprocal",(-4,6),(-4,5)); p.asym_v(1,"x = 1").asym_h(2,"y = 2").curve(f,MUTED,[(-4,.97),(1.03,6)],"y = f(x)")
    p.asym_v(2,"x = 2").asym_h(.5,"y = ½").curve(lambda x:1/f(x),BLUE,[(-4,.97),(1.03,1.97),(2.03,6)],"y = 1/f(x)").point(1,0,"open point",open_=True).point(0,.25,"(0, ¼)").save("example-4-4","A root becomes a vertical asymptote; a vertical asymptote becomes an open point.")

    p=base("Example 4.5(i): y² = (x − 3)²",(-1,7),(-4,5)); p.curve(lambda x:(x-3)**2,MUTED,label="y = (x − 3)²").curve(lambda x:abs(x-3),BLUE,label="y² = (x − 3)²").curve(lambda x:-abs(x-3),BLUE).point(3,0,"(3, 0)").point(2,1,"(2, 1)").point(4,1,"(4, 1)").save("example-4-5a","The transformed graph is y = ±|x − 3|.")
    ints=[(-2*math.pi,-1.5*math.pi),(-.5*math.pi,.5*math.pi),(1.5*math.pi,2*math.pi)]
    p=base("Example 4.5(ii): y² = cos x",(-2*math.pi,2*math.pi),(-1.5,1.5)); p.curve(math.cos,MUTED,label="y = cos x").curve(lambda x:math.sqrt(max(0,math.cos(x))),BLUE,ints,label="y² = cos x").curve(lambda x:-math.sqrt(max(0,math.cos(x))),BLUE,ints).save("example-4-5b","Real transformed points occur only where cos x ≥ 0.")

    # Smooth illustrative curve through the stated roots and intercept, scaled so f(-1)=4.
    f=lambda x:(x+2)*(x-1)*(x-3)*(x*x+x+4)/8
    p=base("Example 4.6: given curve y = f(x)",(-3.2,4.2),(-4,5)); p.curve(f,CORAL).point(-1,4,"(−1, 4)").point(-2,0,"(−2, 0)").point(1,0,"(1, 0)").point(3,0,"(3, 0)").point(0,3,"(0, 3)").save("example-4-6-given","The given curve, reconstructed from all stated stationary points and intercepts.")
    p=base("Example 4.6: y² = f(x)",(-3.2,4.2),(-3,5)); p.curve(f,MUTED,label="y = f(x)")
    intervals=[(-2,1),(3,4.2)]
    p.curve(lambda x:math.sqrt(max(0,f(x))),BLUE,intervals,label="y² = f(x)").curve(lambda x:-math.sqrt(max(0,f(x))),BLUE,intervals)
    for x in (-2,1,3): p.point(x,0,f"({x}, 0)")
    p.point(0,math.sqrt(3),"(0, √3)").point(0,-math.sqrt(3),"(0, −√3)").save("example-4-6","The transformed graph is symmetric about the x-axis and exists where f(x) ≥ 0.")


def rational_plot(name, title, f, xlim, ylim, vertical=(), horizontal=(), oblique=(),
                  points=(), transform=None, extra=None, caption=""):
    """Draw a rational curve and, where requested, its examination transformation."""
    p=base(title,xlim,ylim)
    for x,label in vertical: p.asym_v(x,label)
    for y,label in horizontal: p.asym_h(y,label)
    for fn,label in oblique: p.asym_line(fn,label)
    cuts=sorted(x for x,_ in vertical if xlim[0] < x < xlim[1])
    eps=(xlim[1]-xlim[0])/900
    intervals=[]; left=xlim[0]
    for c in cuts:
        intervals.append((left,c-eps)); left=c+eps
    intervals.append((left,xlim[1]))
    p.curve(f,MUTED if transform else BLUE,intervals,label="y = f(x)")
    if transform == "abs": p.curve(lambda x:abs(f(x)),BLUE,intervals,label="y = |f(x)|")
    elif transform == "even": p.curve(lambda x:f(abs(x)),GREEN,intervals,label="y = f(|x|)")
    elif transform == "reciprocal": p.curve(lambda x:1/f(x),BLUE,intervals,label="y = 1/f(x)")
    elif transform == "square-root":
        p.curve(lambda x:math.sqrt(f(x)),BLUE,intervals,label="y² = f(x)")
        p.curve(lambda x:-math.sqrt(f(x)),BLUE,intervals)
    for x,y,label in points: p.point(x,y,label)
    if extra: extra(p)
    p.save(name,caption or title)


def exercise_figures():
    rational_plot("exercise-4b-q5", "Exercise 4B Q5: p = −1", lambda x:(x*x-x+1)/(x-2),(-5,7),(-7,8),
        [(2,"x = 2")],oblique=[(lambda x:x+1,"y = x + 1")],points=[(0,-.5,"(0, −½)")],caption="No x-intercepts; both branches approach x = 2 and y = x + 1.")
    rational_plot("exercise-4b-q6", "Exercise 4B Q6: k = 4", lambda x:(2*x*x+4*x)/(x+1),(-5,4),(-7,8),
        [(-1,"x = −1")],oblique=[(lambda x:2*x+2,"y = 2x + 2")],points=[(-2,0,"(−2, 0)"),(0,0,"(0, 0)")])
    rational_plot("exercise-4b-q7a", "Exercise 4B Q7: p = 4", lambda x:(4*x*x+4*x+1)/(x+1),(-4,3),(-7,8),
        [(-1,"x = −1")],oblique=[(lambda x:4*x,"y = 4x")],points=[(-.5,0,"(−½, 0)")],caption="The x-axis is tangent at (−1/2, 0).")
    rational_plot("exercise-4b-q7b", "Exercise 4B Q7: p = 1", lambda x:(x*x+4*x+1)/(x+1),(-6,4),(-7,8),
        [(-1,"x = −1")],oblique=[(lambda x:x+3,"y = x + 3")],points=[(-2-math.sqrt(3),0,"−2 − √3"),(-2+math.sqrt(3),0,"−2 + √3")])
    rational_plot("exercise-4b-q8", "Exercise 4B Q8: λ = −1", lambda x:-x+x/(x-2),(-4,7),(-7,7),
        [(2,"x = 2")],oblique=[(lambda x:-x+1,"y = −x + 1")],points=[(0,0,"(0, 0)"),(3,0,"(3, 0)")])


def past_paper_figures():
    # Symbolic-parameter questions use one admissible representative solely to show topology.
    def two_2019(p):
        a=4; f1=lambda x:a*x/(x+5); f2=lambda x:(x*x+(a+10)*x+5*a+26)/(x+5)
        ints=[(-12,-5.02),(-4.98,6)]
        p.asym_v(-5,"x = −5").asym_h(a,"y = a").asym_line(lambda x:x+a+5,"C₂ asymptote")
        p.curve(f1,BLUE,ints,label="C₁").curve(f2,CORAL,ints,label="C₂")
        p.point(-6,a-2,"(−6, a−2)",color=CORAL).point(-4,a+2,"(−4, a+2)",color=CORAL)
    p=base("2019 M/J 11–12 Q10 (representative a = 4)",(-12,6),(-7,12)); two_2019(p); p.save("pp-2019-mj-11-12","The curves do not intersect; a = 4 is used only to display the required general shape.")
    rational_plot("pp-2019-mj-13","2019 M/J 13 Q6 (representative k = 1)",lambda x:x*x/(x-1),(-5,7),(-6,9),[(1,"x = 1")],oblique=[(lambda x:x+1,"y = x + 1")],points=[(0,0,"(0, 0)"),(2,4,"(2, 4)")])
    rational_plot("pp-2019-on","2019 O/N Q4",lambda x:(x*x+1)/(.5*x-.25),(-4,5),(-10,10),[(.5,"x = ½")],oblique=[(lambda x:2*x+1,"y = 2x + 1")],points=[(0,-4,"(0, −4)")])
    rational_plot("pp-2020-mj-q1","2020 M/J 11–12 Q1 (representative a = 2)",lambda x:2*x/(x+7),(-14,10),(-5,6),[(-7,"x = −7")],[(2,"y = a")],points=[(0,0,"(0, 0)")],transform="abs")
    rational_plot("pp-2020-mj-q3","2020 M/J 11–12 Q3",lambda x:x*x/(2*x+1),(-5,5),(-5,5),[(-.5,"x = −½")],oblique=[(lambda x:x/2-.25,"y = x/2 − 1/4")],points=[(-1,-1,"(−1, −1)"),(0,0,"(0, 0)")])
    rational_plot("pp-2020-mj-13","2020 M/J 13 Q6",lambda x:(10+x-2*x*x)/(2*x-3),(-5,7),(-8,8),[(1.5,"x = 3/2")],oblique=[(lambda x:-x-1,"y = −x − 1")],points=[(-2,0,"(−2, 0)"),(2.5,0,"(5/2, 0)"),(0,-10/3,"(0, −10/3)")],transform="abs")
    rational_plot("pp-2020-on-11-13","2020 O/N 11–13 Q6",lambda x:(x*x+x-1)/(x-1),(-5,6),(-6,8),[(1,"x = 1")],oblique=[(lambda x:x+2,"y = x + 2")],points=[(0,1,"(0, 1)")],transform="abs")
    def c23(p):
        f=lambda x:(x-1)/(x-2); ints=[(-5,1.99),(2.01,7)]
        p.asym_v(2,"x = 2").asym_h(1,"y = 1").curve(lambda x:f(x)**2,BLUE,ints,label="C₂").curve(lambda x:abs(f(x)),CORAL,ints,label="C₃").point(1,0,"(a, 0)")
    p=base("2020 O/N 12 Q6 (normalised with a = 1)",(-5,7),(-1,7)); c23(p); p.save("pp-2020-on-12","Normalising a to 1 preserves the required shape and relative positions.")
    specs=[
      ("pp-2021-mj-11-12","2021 M/J 11–12 Q7",lambda x:(x*x+x+9)/(x+1),(-7,7),(-10,11),[(-1,"x = −1")],[],[(lambda x:x,"y = x")],[(2,5,"(2, 5)"),(-4,-7,"(−4, −7)"),(0,9,"(0, 9)")],"abs"),
      ("pp-2021-mj-13","2021 M/J 13 Q7",lambda x:(x*x-x-3)/(1+x-x*x),(-5,5),(-5,5),[((1-math.sqrt(5))/2,"x = (1−√5)/2"),((1+math.sqrt(5))/2,"x = (1+√5)/2")],[(-1,"y = −1")],[],[(.5,-2.6,"(½, −13/5)")],"abs"),
      ("pp-2021-on-11-13","2021 O/N 11–13 Q7",lambda x:(4*x+5)/(4-4*x*x),(-5,5),(-4,5),[(-1,"x = −1"),(1,"x = 1")],[(0,"y = 0")],[],[(-2,.25,"(−2, ¼)"),(-.5,1,"(−½, 1)")],"abs"),
      ("pp-2021-on-12","2021 O/N 12 Q6",lambda x:x*x/(x-3),(-5,9),(-8,16),[(3,"x = 3")],[],[(lambda x:x+3,"y = x + 3")],[(0,0,"(0, 0)")],None),
      ("pp-2022-mj-11-12","2022 M/J 11–12 Q5",lambda x:(2*x*x-x-1)/(x*x+x+1),(-6,5),(-2,4),[],[(2,"y = 2")],[],[(0,-1,"(0, −1)"),(-2,3,"(−2, 3)")],"abs"),
      ("pp-2022-mj-13-q1","2022 M/J 13 Q1",lambda x:(x+1)/(x-1),(-5,5),(-5,5),[(1,"x = 1")],[(1,"y = 1")],[],[(-1,0,"(−1, 0)"),(0,-1,"(0, −1)")],"even"),
      ("pp-2022-mj-13-q3","2022 M/J 13 Q3 (representative a = 1)",lambda x:(x*x+x-1)/(x-1),(-5,6),(-3,8),[(1,"x = 1")],[],[(lambda x:x+2,"y = x + 2")],[(0,1,"(0, 1)"),(2,5,"(2, 5)")],None),
      ("pp-2023-on-11-13","2023 O/N 11–13 Q7",lambda x:(x*x+2)/(x*x-x-2),(-10,6),(-5,5),[(-1,"x = −1"),(2,"x = 2")],[(1,"y = 1")],[],[],"reciprocal"),
      ("pp-2023-on-12","2023 O/N 12 Q7",lambda x:x*x/(x+1),(-6,5),(-7,7),[(-1,"x = −1")],[],[(lambda x:x-1,"y = x − 1")],[(0,0,"(0, 0)"),(-2,-4,"(−2, −4)")],"reciprocal"),
      ("pp-2024-mj-11-12","2024 M/J 11–12 Q6 (a = 3)",lambda x:(x*x+3*x+1)/(x+2),(-7,6),(-8,8),[(-2,"x = −2")],[],[(lambda x:x+1,"y = x + 1")],[(0,.5,"(0, ½)")],"abs"),
      ("pp-2024-mj-13","2024 M/J 13 Q6",lambda x:(x+1)/(x*x+3),(-6,6),(-1.2,1.2),[],[(0,"y = 0")],[],[(-1,0,"(−1, 0)"),(0,1/3,"(0, ⅓)"),(1,.5,"(1, ½)")],"square-root"),
      ("pp-2024-on-11-13","2024 O/N 11–13 Q6",lambda x:(4*x*x+x+1)/(2*x*x-7*x+3),(-4,6),(-6,8),[(.5,"x = ½"),(3,"x = 3")],[(2,"y = 2")],[],[(-1/3,.2,"(−⅓, ⅕)"),(1,-3,"(1, −3)")],"abs"),
      ("pp-2024-on-12","2024 O/N 12 Q6",lambda x:(x*x+3)/(x*x+1),(-5,5),(0,3.5),[],[(1,"y = 1")],[],[(0,3,"(0, 3)")],"reciprocal"),
      ("pp-2025-mj-11-12","2025 M/J 11–12 Q7",lambda x:(2*x*x-5*x)/(2*x*x-7*x-4),(-8,7),(-5,6),[(-.5,"x = −½"),(4,"x = 4")],[(1,"y = 1")],[],[(-5,25/27,"(−5, 25/27)"),(1,1/3,"(1, ⅓)")],"abs"),
      ("pp-2025-mj-13","2025 M/J 13 Q6 (representative a = 2)",lambda x:(x*x+2)/(x+2),(-7,6),(-8,7),[(-2,"x = −a")],[],[(lambda x:x-2,"y = x − a")],[(0,1,"(0, 1)")],"abs"),
      ("pp-2025-mj-14","2025 M/J 14 Q7",lambda x:(x*x+x-4)/(x*x+x+2),(-6,6),(-3,2),[],[(1,"y = 1")],[],[],"even"),
      ("pp-2025-on-11-13","2025 O/N 11–13 Q7",lambda x:(x+2)/(x*x+3*x+1),(-6,4),(-6,6),[((-3-math.sqrt(5))/2,"left asymptote"),((-3+math.sqrt(5))/2,"right asymptote")],[(0,"y = 0")],[],[(-2,0,"(−2, 0)"),(0,2,"(0, 2)")],"abs"),
      ("pp-2025-on-12","2025 O/N 12 Q7",lambda x:(x*x+x+1)/(x+1),(-6,5),(-7,7),[(-1,"x = −1")],[],[(lambda x:x,"y = x")],[(0,1,"(0, 1)"),(-2,-3,"(−2, −3)")],"even"),
      ("pp-2025-on-14","2025 O/N 14 Q7",lambda x:(10*x*x-11*x-18)/(10*x-18),(-5,6),(-8,8),[(1.8,"x = 9/5")],[],[(lambda x:x+.7,"y = x + 7/10")],[(-.9,0,"(−9/10, 0)"),(2,0,"(2, 0)"),(0,1,"(0, 1)")],"abs")]
    for args in specs:
        rational_plot(*args)


def audit_generated_figures():
    expected=12+5+22
    actual=len(list(OUT.glob("*.svg")))
    if actual < expected: raise RuntimeError(f"Expected at least {expected} SVGs, found {actual}")


if __name__ == "__main__":
    examples()
    exercise_figures()
    past_paper_figures()
    audit_generated_figures()
    print(f"Generated {len(list(OUT.glob('*.svg')))} SVG files in {OUT}")
