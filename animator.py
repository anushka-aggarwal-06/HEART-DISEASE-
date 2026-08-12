"""
animator.py
-----------
Lightweight, dependency-free animation helpers built purely on top of
tkinter's `.after()` scheduler. Every animation is non-blocking so the
UI thread never freezes.
"""

import math


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2


class Animator:
    """Static helpers that animate CTk / tk widgets over time."""

    # ------------------------------------------------------------------
    # Fade a toplevel / CTk window in via alpha channel
    # ------------------------------------------------------------------
    @staticmethod
    def fade_in_window(window, duration_ms: int = 500, steps: int = 25, on_done=None):
        interval = max(1, duration_ms // steps)

        def _step(i=0):
            progress = ease_out_cubic(i / steps)
            try:
                window.attributes("-alpha", progress)
            except Exception:
                pass
            if i < steps:
                window.after(interval, lambda: _step(i + 1))
            elif on_done:
                on_done()

        _step()

    # ------------------------------------------------------------------
    # Slide + fade a widget upward into place (using .place geometry)
    # ------------------------------------------------------------------
    @staticmethod
    def slide_up(widget, target_rely, start_offset=0.08, duration_ms=550, steps=30, on_done=None):
        interval = max(1, duration_ms // steps)
        start_rely = target_rely + start_offset

        def _step(i=0):
            t = ease_out_cubic(i / steps)
            current_rely = start_rely + (target_rely - start_rely) * t
            try:
                widget.place_configure(rely=current_rely)
            except Exception:
                return
            if i < steps:
                widget.after(interval, lambda: _step(i + 1))
            elif on_done:
                on_done()

        _step()

    # ------------------------------------------------------------------
    # Horizontal shake -> used for validation errors
    # ------------------------------------------------------------------
    @staticmethod
    def shake(widget, relx, amplitude=0.012, duration_ms=380, cycles=5):
        interval = max(1, duration_ms // cycles)

        def _step(i=0):
            if i > cycles:
                widget.place_configure(relx=relx)
                return
            offset = amplitude * math.sin(i * math.pi) * (-1 if i % 2 == 0 else 1)
            widget.place_configure(relx=relx + offset)
            widget.after(interval, lambda: _step(i + 1))

        _step()

    # ------------------------------------------------------------------
    # Generic numeric tween -> calls `on_update(value)` every frame
    # ------------------------------------------------------------------
    @staticmethod
    def tween(widget, start, end, duration_ms, on_update, on_done=None, steps=30, easing=ease_in_out_quad):
        interval = max(1, duration_ms // steps)

        def _step(i=0):
            t = easing(i / steps)
            value = start + (end - start) * t
            on_update(value)
            if i < steps:
                widget.after(interval, lambda: _step(i + 1))
            elif on_done:
                on_done()

        _step()

    # ------------------------------------------------------------------
    # Continuous pulse loop -> returns a stop() function
    # ------------------------------------------------------------------
    @staticmethod
    def pulse_loop(widget, on_frame, period_ms=1400, fps=30):
        interval = max(1, 1000 // fps)
        state = {"running": True, "t": 0.0}
        step_inc = interval / period_ms

        def _step():
            if not state["running"]:
                return
            phase = (math.sin(state["t"] * 2 * math.pi) + 1) / 2  # 0..1
            on_frame(phase)
            state["t"] = (state["t"] + step_inc) % 1.0
            widget.after(interval, _step)

        _step()

        def stop():
            state["running"] = False

        return stop


class Spinner:
    """A small rotating-arc loading spinner drawn on a tk.Canvas."""

    def __init__(self, canvas, cx, cy, radius=14, color="#2563EB", width=3):
        self.canvas = canvas
        self.cx, self.cy, self.radius = cx, cy, radius
        self.color = color
        self.width = width
        self.angle = 0
        self.running = False
        self.arc_id = None

    def start(self):
        self.running = True
        self.arc_id = self.canvas.create_arc(
            self.cx - self.radius, self.cy - self.radius,
            self.cx + self.radius, self.cy + self.radius,
            start=self.angle, extent=110,
            style="arc", outline=self.color, width=self.width,
        )
        self._animate()

    def _animate(self):
        if not self.running:
            return
        self.angle = (self.angle + 12) % 360
        if self.arc_id:
            self.canvas.itemconfigure(self.arc_id, start=self.angle)
        self.canvas.after(20, self._animate)

    def stop(self):
        self.running = False
        if self.arc_id:
            try:
                self.canvas.delete(self.arc_id)
            except Exception:
                pass
            self.arc_id = None
