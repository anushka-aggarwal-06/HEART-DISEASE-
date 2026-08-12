"""
background.py
--------------
An animated tkinter Canvas that renders the AI + Healthcare themed
background used behind every auth screen:

    - Soft blue -> cyan gradient
    - Slowly floating AI particles
    - A neural-network of connected nodes
    - A subtle DNA helix outline
    - Faint medical cross glyphs
    - A slow-moving animated ECG heartbeat waveform
    - Soft glowing circles

Everything is intentionally subtle (low opacity colours, thin strokes)
so it never competes with the foreground glass card.
"""

import math
import random
import tkinter as tk

from utils.theme import COLORS


class AnimatedBackground(tk.Canvas):
    def __init__(self, master, width=1180, height=760, **kwargs):
        super().__init__(
            master, width=width, height=height,
            highlightthickness=0, bd=0, bg=COLORS["bg"], **kwargs
        )
        self.width = width
        self.height = height
        self._running = False

        self.particles = []
        self.neural_nodes = []
        self.ecg_offset = 0

        self._build_static_layers()
        self._init_particles()
        self._init_neural_nodes()

    # ------------------------------------------------------------------
    # Static (drawn once) decorative layers
    # ------------------------------------------------------------------
    def _build_static_layers(self):
        self._draw_gradient()
        self._draw_glow_circles()
        self._draw_dna_helix()
        self._draw_medical_crosses()

    def _draw_gradient(self):
        """Vertical blue -> cyan tinted gradient using thin bands."""
        top = (0xF8, 0xFC, 0xFF)
        bottom = (0xEA, 0xF6, 0xFF)
        steps = 120
        for i in range(steps):
            t = i / steps
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(self.height * i / steps)
            y1 = int(self.height * (i + 1) / steps)
            self.create_rectangle(0, y0, self.width, y1, fill=color, outline="")

    def _draw_glow_circles(self):
        spots = [
            (self.width * 0.18, self.height * 0.22, 160, COLORS["glow"]),
            (self.width * 0.85, self.height * 0.18, 190, "#E3D6FF"),
            (self.width * 0.12, self.height * 0.85, 170, "#CFF3FF"),
            (self.width * 0.88, self.height * 0.82, 200, COLORS["glow"]),
        ]
        for cx, cy, r, color in spots:
            for i, alpha_r in enumerate([r, r * 0.7, r * 0.45]):
                self.create_oval(
                    cx - alpha_r, cy - alpha_r, cx + alpha_r, cy + alpha_r,
                    fill=color, outline="", stipple="gray25" if i == 0 else "gray12"
                )

    def _draw_dna_helix(self):
        """A faint decorative double-helix outline near the left edge."""
        x_center = self.width * 0.06
        amplitude = 34
        points_a, points_b = [], []
        for y in range(0, self.height, 6):
            phase = y / 55
            xa = x_center + amplitude * math.sin(phase)
            xb = x_center + amplitude * math.sin(phase + math.pi)
            points_a.extend([xa, y])
            points_b.extend([xb, y])
        if len(points_a) >= 4:
            self.create_line(*points_a, fill="#C9E4FF", width=2, smooth=True)
        if len(points_b) >= 4:
            self.create_line(*points_b, fill="#DCEBFF", width=2, smooth=True)
        # rungs
        for y in range(0, self.height, 26):
            phase = y / 55
            xa = x_center + amplitude * math.sin(phase)
            xb = x_center + amplitude * math.sin(phase + math.pi)
            self.create_line(xa, y, xb, y, fill="#DCEBFF", width=1)

    def _draw_medical_crosses(self):
        random.seed(7)
        positions = [(random.uniform(0.25, 0.95) * self.width,
                      random.uniform(0.05, 0.95) * self.height) for _ in range(6)]
        for x, y in positions:
            s = 9
            self.create_rectangle(x - s, y - s / 3, x + s, y + s / 3, fill="#DCEEFF", outline="")
            self.create_rectangle(x - s / 3, y - s, x + s / 3, y + s, fill="#DCEEFF", outline="")

    # ------------------------------------------------------------------
    # Particles (floating AI dots)
    # ------------------------------------------------------------------
    def _init_particles(self):
        random.seed(3)
        for _ in range(26):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            r = random.uniform(1.5, 3.2)
            speed = random.uniform(0.15, 0.5)
            angle = random.uniform(0, 2 * math.pi)
            color = random.choice([COLORS["primary"], COLORS["cyan"], COLORS["purple"]])
            item = self.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="", stipple="gray50")
            self.particles.append({"id": item, "x": x, "y": y, "r": r, "speed": speed, "angle": angle})

    def _init_neural_nodes(self):
        random.seed(11)
        cols, rows = 5, 4
        margin_x, margin_y = self.width * 0.55, self.height * 0.1
        for c in range(cols):
            for r in range(rows):
                if random.random() < 0.55:
                    x = margin_x + c * (self.width * 0.4 / cols) + random.uniform(-14, 14)
                    y = margin_y + r * (self.height * 0.6 / rows) + random.uniform(-14, 14)
                    self.neural_nodes.append({"x": x, "y": y})

        # connecting lines (drawn once, faint)
        for i, n1 in enumerate(self.neural_nodes):
            for n2 in self.neural_nodes[i + 1:]:
                dist = math.hypot(n1["x"] - n2["x"], n1["y"] - n2["y"])
                if dist < 130:
                    self.create_line(n1["x"], n1["y"], n2["x"], n2["y"], fill="#DCEAFB", width=1)

        for n in self.neural_nodes:
            n["id"] = self.create_oval(
                n["x"] - 3, n["y"] - 3, n["x"] + 3, n["y"] + 3,
                fill=COLORS["primary"], outline="", stipple="gray25"
            )

    # ------------------------------------------------------------------
    # ECG waveform (redrawn each frame, moves left)
    # ------------------------------------------------------------------
    def _ecg_pattern(self, length):
        """One heartbeat cycle as a list of relative (dx, dy) samples."""
        pattern = []
        cycle = 90
        for i in range(cycle):
            t = i / cycle
            if 0.35 < t < 0.42:
                y = -46
            elif 0.42 <= t < 0.46:
                y = 26
            elif 0.46 <= t < 0.5:
                y = -10
            else:
                y = 0
            pattern.append(y)
        reps = length // cycle + 2
        return (pattern * reps)

    def _draw_ecg(self):
        y_base = self.height * 0.93
        full = self._ecg_pattern(self.width + 60)
        offset = int(self.ecg_offset) % 90
        coords = []
        x = -60
        for i in range(len(full) - offset):
            val = full[i + offset]
            coords.extend([x, y_base + val])
            x += 8
            if x > self.width + 20:
                break
        if hasattr(self, "_ecg_id") and self._ecg_id:
            self.delete(self._ecg_id)
        if len(coords) >= 4:
            self._ecg_id = self.create_line(
                *coords, fill=COLORS["error"], width=2, smooth=False, joinstyle="round"
            )
        else:
            self._ecg_id = None

    # ------------------------------------------------------------------
    # Animation loop
    # ------------------------------------------------------------------
    def start(self):
        if self._running:
            return
        self._running = True
        self._animate()

    def stop(self):
        self._running = False

    def _animate(self):
        if not self._running:
            return

        # move particles
        for p in self.particles:
            p["x"] += math.cos(p["angle"]) * p["speed"]
            p["y"] += math.sin(p["angle"]) * p["speed"]
            if p["x"] < -5 or p["x"] > self.width + 5 or p["y"] < -5 or p["y"] > self.height + 5:
                p["x"], p["y"] = random.uniform(0, self.width), self.height + 5
                p["angle"] = random.uniform(-math.pi, 0)
            r = p["r"]
            self.coords(p["id"], p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r)

        # ECG heartbeat moves right to left
        self.ecg_offset += 1.2
        self._draw_ecg()

        self.after(40, self._animate)
