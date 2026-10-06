"""Generate assets/timeline.svg (zig-zag journey timeline) from data/timeline.json."""
import json, math, pathlib, textwrap
from xml.sax.saxutils import escape

root = pathlib.Path(__file__).resolve().parent.parent
items = sorted(json.loads((root / "data/timeline.json").read_text(encoding="utf-8")),
               key=lambda x: x["date"])
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
COLORS = ["#FDB913", "#E53935", "#9C1A8A", "#2F5D9E", "#0E8A8F", "#F57C00", "#43A047"]

GAP, STEP, DIP, BASE, R = 190, 50, 80, 400, 30
LEFT = 90
FONT = "Georgia, 'Times New Roman', serif"

pts = []
for i in range(len(items)):
    x = LEFT + i * GAP
    y = BASE - i * STEP + (DIP if i % 2 else 0)
    pts.append((x, y))

parts, ys = [], []

# road
road = " ".join(f"{x},{y}" for x, y in pts)
lx, ly = pts[-1]
px, py = pts[-2] if len(pts) > 1 else (lx - GAP, ly)
ux, uy = 1, -0.6
n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
ex, ey = lx + ux * 110, ly + uy * 110
tx, ty = lx + ux * 160, ly + uy * 160
nx, ny = -uy, ux
head = f"{tx},{ty} {ex + nx*34},{ey + ny*34} {ex - nx*34},{ey - ny*34}"
parts.append(f'<polyline points="{road} {ex},{ey}" fill="none" stroke="#9e9e9e" '
             f'stroke-width="24" stroke-linejoin="round" stroke-linecap="round"/>')
parts.append(f'<polygon points="{head}" fill="#9e9e9e" stroke="#9e9e9e" stroke-width="6" stroke-linejoin="round"/>')
ys += [ty, ey + ny*34, ey - ny*34]

# nodes + labels
for i, (it, (x, y)) in enumerate(zip(items, pts)):
    col = COLORS[i % len(COLORS)]
    parts.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="#b5b5b5"/>')
    parts.append(f'<circle cx="{x}" cy="{y}" r="{R-6}" fill="{col}" stroke="#fff" stroke-width="3"/>')
    parts.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="17" font-weight="bold" fill="#fff">{i+1:02d}</text>')
    year, month = it["date"][:4], int(it["date"][5:7]) if len(it["date"]) >= 7 else None
    when = f"{MONTHS[month-1]} {year}" if month else year
    lines = textwrap.wrap(it["title"], 24)[:4]
    block_h = 20 + 17 * len(lines)
    above = i % 2 == 1
    anchor, tx_ = ("end", x + 22) if above else ("start", x - 22)
    top = (y - R - 22 - block_h) if above else (y + R + 22)
    parts.append(f'<text x="{tx_}" y="{top+16}" text-anchor="{anchor}" font-family="{FONT}" '
                 f'font-size="18" font-weight="bold" class="t">{escape(when)}</text>')
    for j, ln in enumerate(lines):
        parts.append(f'<text x="{tx_}" y="{top+38+17*j}" text-anchor="{anchor}" '
                     f'font-family="{FONT}" font-size="13" class="c">{escape(ln)}</text>')
    ys += [top, top + block_h, y - R, y + R]

pad_top = 70
shift = pad_top - min(ys)
height = int(max(ys) + shift + 30)
width = int(max(tx, LEFT + (len(items) - 1) * GAP + 260) + 40)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  .t {{ fill: #222; }} .c {{ fill: #555; }} .h {{ fill: #222; }}
  @media (prefers-color-scheme: dark) {{ .t, .h {{ fill: #f2f2f2; }} .c {{ fill: #bdbdbd; }} }}
</style>
<text x="{width/2}" y="38" text-anchor="middle" font-family="{FONT}" font-size="26" class="h">Journey Timeline</text>
<g transform="translate(0,{shift})">
{chr(10).join(parts)}
</g>
</svg>'''

out = root / "assets/timeline.svg"
out.parent.mkdir(exist_ok=True)
out.write_text(svg, encoding="utf-8")
print(f"Wrote {out} ({width}x{height}, {len(items)} events)")
