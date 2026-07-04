"""
Graph Network Visualization
============================

Generates an interactive HTML visualization of the identity graph
using standalone JavaScript (no external dependencies).

Usage:
    from src.graph_viz import generate_graph_html
    html = generate_graph_html("output/identity_graph.json")
    with open("output/graph.html", "w") as f:
        f.write(html)
"""

import json
import os
from typing import Optional


def generate_graph_html(graph_path: str, output_path: str = None) -> str:
    """Generate interactive HTML graph visualization."""
    with open(graph_path) as f:
        graph = json.load(f)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", graph.get("connections", []))

    # Prepare node data for JS
    node_js = []
    for node in nodes:
        node_id = node.get("id", node.get("name", ""))
        label = node.get("name", node.get("id", ""))
        resonance = node.get("resonance", node.get("analytics", {}).get("composite_resonance", 50))
        node_js.append({
            "id": node_id,
            "label": label,
            "resonance": resonance,
        })

    edge_js = []
    for edge in edges:
        source = edge.get("source", edge.get("from", ""))
        target = edge.get("target", edge.get("to", ""))
        weight = edge.get("weight", edge.get("similarity", 0.5))
        edge_js.append({"source": source, "target": target, "weight": weight})

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Identity Network Graph</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0a0a0a; font-family: 'SF Mono', monospace; color: #fff; overflow: hidden; }}
canvas {{ display: block; }}
#info {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 12px; border-radius: 6px; border: 1px solid #333; font-size: 11px; }}
#info h3 {{ color: #4fc3f7; margin-bottom: 4px; font-size: 13px; }}
#tooltip {{ position: absolute; display: none; background: rgba(0,0,0,0.9); padding: 8px 12px; border-radius: 4px; border: 1px solid #4fc3f7; font-size: 11px; pointer-events: none; }}
</style>
</head>
<body>
<div id="info">
  <h3>Identity Network</h3>
  <p>{len(nodes)} nodes, {len(edges)} edges</p>
  <p>Drag to move. Scroll to zoom. Hover for details.</p>
</div>
<div id="tooltip"></div>
<canvas id="canvas"></canvas>
<script>
const nodes = {json.dumps(node_js)};
const edges = {json.dumps(edge_js)};

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

let W, H, scale = 1, offsetX = 0, offsetY = 0;
let dragging = null, dragStart = {{x: 0, y: 0}};
let mouseX = 0, mouseY = 0;

function resize() {{
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}}
resize();
window.addEventListener('resize', resize);

// Initialize positions in circle
const cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.35;
nodes.forEach((n, i) => {{
  const angle = (2 * Math.PI * i) / nodes.length;
  n.x = cx + R * Math.cos(angle);
  n.y = cy + R * Math.sin(angle);
  n.vx = 0;
  n.vy = 0;
}});

function getNode(id) {{ return nodes.find(n => n.id === id); }}

function tick() {{
  // Simple force simulation
  for (let i = 0; i < nodes.length; i++) {{
    for (let j = i + 1; j < nodes.length; j++) {{
      const dx = nodes[j].x - nodes[i].x;
      const dy = nodes[j].y - nodes[i].y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = 2000 / (d * d);
      nodes[i].vx -= (dx / d) * force;
      nodes[i].vy -= (dy / d) * force;
      nodes[j].vx += (dx / d) * force;
      nodes[j].vy += (dy / d) * force;
    }}
  }}
  // Edge attraction
  edges.forEach(e => {{
    const a = getNode(e.source), b = getNode(e.target);
    if (!a || !b) return;
    const dx = b.x - a.x, dy = b.y - a.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const force = (d - 100) * 0.01 * e.weight;
    a.vx += (dx / d) * force;
    a.vy += (dy / d) * force;
    b.vx -= (dx / d) * force;
    b.vy -= (dy / d) * force;
  }});
  // Center gravity
  nodes.forEach(n => {{
    n.vx += (W/2 - n.x) * 0.001;
    n.vy += (H/2 - n.y) * 0.001;
    n.vx *= 0.9;
    n.vy *= 0.9;
    if (n !== dragging) {{
      n.x += n.vx;
      n.y += n.vy;
    }}
  }});
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.save();
  ctx.translate(offsetX, offsetY);
  ctx.scale(scale, scale);

  // Draw edges
  edges.forEach(e => {{
    const a = getNode(e.source), b = getNode(e.target);
    if (!a || !b) return;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = `rgba(79, 195, 247, ${{e.weight * 0.3}})`;
    ctx.lineWidth = e.weight * 2;
    ctx.stroke();
  }});

  // Draw nodes
  nodes.forEach(n => {{
    const r = 8 + (n.resonance || 50) / 10;
    const hue = ((n.resonance || 50) / 100) * 120 + 180;
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${{hue}}, 70%, 50%)`;
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#ccc';
    ctx.font = '9px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(n.label, n.x, n.y - r - 4);
  }});

  ctx.restore();
}}

function loop() {{
  tick();
  draw();
  requestAnimationFrame(loop);
}}
loop();

// Interaction
canvas.addEventListener('mousedown', e => {{
  const mx = (e.clientX - offsetX) / scale;
  const my = (e.clientY - offsetY) / scale;
  dragging = nodes.find(n => Math.hypot(n.x - mx, n.y - my) < 20);
  if (dragging) {{ dragStart = {{x: mx - dragging.x, y: my - dragging.y}}; }}
}});

canvas.addEventListener('mousemove', e => {{
  mouseX = e.clientX;
  mouseY = e.clientY;
  if (dragging) {{
    const mx = (e.clientX - offsetX) / scale;
    const my = (e.clientY - offsetY) / scale;
    dragging.x = mx - dragStart.x;
    dragging.y = my - dragStart.y;
    dragging.vx = 0; dragging.vy = 0;
  }}
  // Tooltip
  const mx = (e.clientX - offsetX) / scale;
  const my = (e.clientY - offsetY) / scale;
  const hover = nodes.find(n => Math.hypot(n.x - mx, n.y - my) < 20);
  if (hover) {{
    tooltip.style.display = 'block';
    tooltip.style.left = (e.clientX + 12) + 'px';
    tooltip.style.top = (e.clientY + 12) + 'px';
    tooltip.innerHTML = `<b>${{hover.label}}</b><br>Resonance: ${{(hover.resonance || 0).toFixed(1)}}`;
  }} else {{
    tooltip.style.display = 'none';
  }}
}});

canvas.addEventListener('mouseup', () => {{ dragging = null; }});

canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.9 : 1.1;
  scale *= factor;
  offsetX = mouseX - (mouseX - offsetX) * factor;
  offsetY = mouseY - (mouseY - offsetY) * factor;
}});
</script>
</body>
</html>"""

    if output_path:
        with open(output_path, "w") as f:
            f.write(html)

    return html
