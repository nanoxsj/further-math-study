from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "paper-1" / "figures" / "matrices"
OUT.mkdir(parents=True, exist_ok=True)


def wrap(title: str, body: str, caption: str, view="0 0 560 360") -> str:
    marker_id = "arrow-" + str(sum((i + 1) * ord(ch) for i, ch in enumerate(title)))
    return f'''<figure class="math-figure">
<svg viewBox="{view}" role="img" aria-label="{title}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="{marker_id}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker>
    <style>
      .axis{{stroke:#475569;stroke-width:1.6;marker-end:url(#{marker_id})}}
      .grid{{stroke:#cbd5e1;stroke-width:1;stroke-dasharray:4 5}}
      .shape{{fill:#38bdf826;stroke:#0284c7;stroke-width:3;stroke-linejoin:round}}
      .image{{fill:#f9731626;stroke:#ea580c;stroke-width:3;stroke-linejoin:round}}
      .line1{{stroke:#7c3aed;stroke-width:3}}
      .line2{{stroke:#16a34a;stroke-width:3}}
      .point{{fill:#0f172a}}
      .label{{font:15px system-ui,sans-serif;fill:#334155}}
      .small{{font:13px system-ui,sans-serif;fill:#475569}}
    </style>
  </defs>
{body}
</svg>
<figcaption>{caption}</figcaption>
</figure>'''


axes = '''  <line class="axis" x1="45" y1="300" x2="525" y2="300"/>
  <line class="axis" x1="280" y1="330" x2="280" y2="35"/>
  <text class="label" x="530" y="305">x</text><text class="label" x="286" y="32">y</text>
  <text class="small" x="266" y="318">O</text>'''


figures = {
    "example-1-5.svg": wrap(
        "Reflection in the x-axis followed by enlargement scale factor 3",
        axes + '''
  <polygon class="shape" points="290,290 310,290 300,275"/>
  <polygon class="image" points="310,330 370,330 340,375"/>
  <line class="grid" x1="45" y1="300" x2="525" y2="300"/>
  <text class="label" x="302" y="270">S</text><text class="label" x="375" y="360">T(S)</text>
  <text class="small" x="52" y="52">reflection in x-axis, then enlargement ×3</text>''',
        "Example 1.5: the reflected image lies below the x-axis and every distance from the origin is tripled.",
    ),
    "example-1-7.svg": wrap(
        "Unit rectangle and its image under a shear",
        axes + '''
  <polygon class="shape" points="280,300 400,300 400,210 280,210"/>
  <polygon class="image" points="280,300 400,300 490,210 370,210"/>
  <text class="label" x="320" y="200">original</text><text class="label" x="430" y="200">image</text>
  <line class="grid" x1="370" y1="210" x2="370" y2="300"/>
  <line class="grid" x1="490" y1="210" x2="490" y2="300"/>
  <text class="small" x="52" y="52">x-axis fixed; horizontal displacement is proportional to y</text>''',
        "Example 1.7: a shear preserves height and area while slanting the vertical sides.",
    ),
    "example-1-11.svg": wrap(
        "Two invariant lines through the origin",
        axes + '''
  <line class="line1" x1="80" y1="500" x2="500" y2="80"/>
  <line class="line2" x1="180" y1="40" x2="360" y2="400"/>
  <circle class="point" cx="280" cy="300" r="4"/>
  <text class="label" x="438" y="112">y = x</text>
  <text class="label" x="190" y="67">y = −2x</text>
  <text class="small" x="52" y="52">points may move, but each whole line maps onto itself</text>''',
        "Example 1.11: an invariant line need not be a line of invariant points.",
    ),
    "example-6-2.svg": wrap(
        "Unit square transformed to a parallelogram",
        axes + '''
  <polygon class="shape" points="280,300 360,300 360,220 280,220"/>
  <polygon class="image" points="280,300 430,265 470,155 320,190"/>
  <text class="label" x="312" y="214">S</text><text class="label" x="418" y="170">M(S)</text>
  <text class="small" x="52" y="52">area image = |det M| × area original</text>''',
        "Example 6.2: the determinant gives the signed area factor; its absolute value gives the area scale factor.",
    ),
    "past-2020-on-12.svg": wrap(
        "Invariant lines of a reflection matrix",
        axes + '''
  <line class="line1" x1="55" y1="360" x2="520" y2="235"/>
  <line class="line2" x1="235" y1="30" x2="325" y2="355"/>
  <circle class="point" cx="280" cy="300" r="4"/>
  <text class="label" x="395" y="248">y = (2 − √3)x</text>
  <text class="label" x="58" y="75">y = −(2 + √3)x</text>''',
        "2020 O/N 12 Q4: the two invariant directions are perpendicular, as expected for a reflection.",
    ),
    "past-2023-on-12.svg": wrap(
        "Unit square mapped by a shear and stretch",
        axes + '''
  <polygon class="shape" points="280,300 350,300 350,230 280,230"/>
  <polygon class="image" points="280,300 440,255 440,185 280,230"/>
  <line class="line1" x1="95" y1="350" x2="510" y2="145"/>
  <text class="label" x="375" y="150">y = x/(k − 1)</text>
  <text class="small" x="52" y="52">schematic for k &gt; 1; the purple direction maps to itself</text>''',
        "2023 O/N 12 Q3: the image is a parallelogram and the marked direction is invariant.",
    ),
}

for name, content in figures.items():
    (OUT / name).write_text(content, encoding="utf-8")

print(f"generated {len(figures)} SVG fragments in {OUT}")
