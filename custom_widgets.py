"""
custom_widgets.py
------------------
Premium, reusable CustomTkinter components shared by the Login and
Signup screens: glowing inputs, lift/shrink buttons, the animated
heartbeat logo, a password-strength meter and toast-style popups.
"""

import tkinter as tk
import customtkinter as ctk

from utils.theme import COLORS, FONTS, RADIUS
from utils.validators import password_requirements
from animations.animator import Animator


# ==========================================================================
# GLOW INPUT FIELD
# ==========================================================================
class GlowEntry(ctk.CTkFrame):
    """A labelled input with an icon, focus glow border and optional
    show/hide password toggle."""

    def __init__(self, master, label_text, icon="•", placeholder="",
                 show=None, is_password=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.is_password = is_password
        self._revealed = False

        self.label = ctk.CTkLabel(
            self, text=label_text, font=ctk.CTkFont(*FONTS["field_label"]),
            text_color=COLORS["text"], anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 6))

        self.field_wrapper = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=RADIUS["input"],
            border_width=1.5, border_color=COLORS["border"], height=46
        )
        self.field_wrapper.pack(fill="x")
        self.field_wrapper.pack_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.field_wrapper, text=icon, font=ctk.CTkFont(size=15),
            text_color=COLORS["primary"], width=28
        )
        self.icon_label.pack(side="left", padx=(12, 0))

        self.entry = ctk.CTkEntry(
            self.field_wrapper, placeholder_text=placeholder,
            font=ctk.CTkFont(*FONTS["body"]), border_width=0,
            fg_color="transparent", text_color=COLORS["text"],
            show=show,
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=(6, 6), pady=6)

        self.toggle_btn = None
        if self.is_password:
            self.toggle_btn = ctk.CTkLabel(
                self.field_wrapper, text="Show", font=ctk.CTkFont(*FONTS["small"]),
                text_color=COLORS["primary"], cursor="hand2", width=40
            )
            self.toggle_btn.pack(side="right", padx=(0, 12))
            self.toggle_btn.bind("<Button-1>", self._toggle_visibility)

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        self.error_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(*FONTS["small"]),
            text_color=COLORS["error"], anchor="w", height=16
        )
        self.error_label.pack(fill="x", pady=(3, 0))

    # ------------------------------------------------------------------
    def _on_focus_in(self, _event=None):
        self.field_wrapper.configure(border_color=COLORS["primary"], border_width=2)

    def _on_focus_out(self, _event=None):
        self.field_wrapper.configure(border_color=COLORS["border"], border_width=1.5)

    def _toggle_visibility(self, _event=None):
        self._revealed = not self._revealed
        self.entry.configure(show="" if self._revealed else "*")
        self.toggle_btn.configure(text="Hide" if self._revealed else "Show")

    # ------------------------------------------------------------------
    def get(self) -> str:
        return self.entry.get()

    def set_error(self, message: str):
        self.error_label.configure(text=message)
        if message:
            self.field_wrapper.configure(border_color=COLORS["error"], border_width=2)
        else:
            self.field_wrapper.configure(border_color=COLORS["border"], border_width=1.5)

    def clear_error(self):
        self.set_error("")


# ==========================================================================
# GRADIENT / ANIMATED BUTTON  (hover-lift + click-shrink simulation)
# ==========================================================================
class GradientButton(ctk.CTkButton):
    """A CTkButton with a soft-glow hover state and a quick 'press' shrink
    effect, giving the illusion of a lifted, tactile premium button."""

    def __init__(self, master, text, command=None, style="primary", **kwargs):
        colors = {
            "primary": (COLORS["primary"], "#1D4ED8"),
            "outline": (COLORS["card"], COLORS["bg_secondary"]),
        }
        fg, hover = colors.get(style, colors["primary"])
        text_color = COLORS["white"] if style == "primary" else COLORS["primary"]
        border_width = 0 if style == "primary" else 1.5

        super().__init__(
            master, text=text, command=command,
            fg_color=fg, hover_color=hover, text_color=text_color,
            corner_radius=RADIUS["button"], font=ctk.CTkFont(*FONTS["button"]),
            height=46, border_width=border_width, border_color=COLORS["primary"],
            **kwargs
        )
        self._base_height = 46
        self.bind("<ButtonPress-1>", self._on_press, add="+")
        self.bind("<ButtonRelease-1>", self._on_release, add="+")

    def _on_press(self, _event=None):
        self.configure(height=self._base_height - 3)

    def _on_release(self, _event=None):
        self.after(80, lambda: self.configure(height=self._base_height))


# ==========================================================================
# HEARTBEAT LOGO  (canvas heart icon with pulsing glow ring)
# ==========================================================================
class HeartbeatLogo(ctk.CTkFrame):
    def __init__(self, master, size=90, **kwargs):
        super().__init__(master, fg_color="transparent", width=size, height=size, **kwargs)
        self.size = size
        self.canvas = tk.Canvas(
            self, width=size, height=size, highlightthickness=0, bd=0,
            bg=COLORS["card"]
        )
        self.canvas.pack()
        self._draw_heart()
        self._stop_pulse = None

    def _draw_heart(self):
        c = self.size / 2
        s = self.size * 0.30
        # glow ring (updated by pulse)
        self.glow_id = self.canvas.create_oval(
            c - s * 1.6, c - s * 1.6, c + s * 1.6, c + s * 1.6,
            outline=COLORS["cyan"], width=2
        )
        # heart shape via two circles + triangle
        self.canvas.create_oval(c - s, c - s * 0.7, c, c + s * 0.3, fill=COLORS["primary"], outline="")
        self.canvas.create_oval(c, c - s * 0.7, c + s, c + s * 0.3, fill=COLORS["primary"], outline="")
        self.canvas.create_polygon(
            c - s, c - s * 0.05,
            c + s, c - s * 0.05,
            c, c + s * 1.05,
            fill=COLORS["primary"], outline=""
        )

    def start_pulse(self):
        def _frame(phase):
            scale = 1.0 + phase * 0.18
            c = self.size / 2
            s = self.size * 0.30 * 1.6 * scale
            self.canvas.coords(self.glow_id, c - s, c - s, c + s, c + s)
        self._stop_pulse = Animator.pulse_loop(self.canvas, _frame, period_ms=1300)

    def stop_pulse(self):
        if self._stop_pulse:
            self._stop_pulse()


# ==========================================================================
# PASSWORD STRENGTH METER
# ==========================================================================
class PasswordStrengthBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bar = ctk.CTkProgressBar(
            self, height=6, corner_radius=3, progress_color=COLORS["error"],
            fg_color=COLORS["border"]
        )
        self.bar.pack(fill="x", pady=(4, 2))
        self.bar.set(0)
        self.label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(*FONTS["small"]), text_color=COLORS["text_secondary"]
        )
        self.label.pack(anchor="w")

    def update_strength(self, score: int, label: str, color_key: str):
        self.bar.set(score / 4)
        self.bar.configure(progress_color=COLORS.get(color_key, COLORS["primary"]))
        self.label.configure(text=f"Password strength: {label}" if label else "")


# ==========================================================================
# PASSWORD REQUIREMENTS CHECKLIST
# ==========================================================================
class PasswordRequirementsChecklist(ctk.CTkFrame):
    """Live ✓/○ checklist shown under the password field while typing."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._rows = []
        for label, _met in password_requirements(""):
            row = ctk.CTkLabel(
                self, text=f"○  {label}", font=ctk.CTkFont(*FONTS["small"]),
                text_color=COLORS["text_secondary"], anchor="w"
            )
            row.pack(fill="x", pady=1)
            self._rows.append(row)

    def update_checklist(self, password: str):
        for row, (label, met) in zip(self._rows, password_requirements(password)):
            if met:
                row.configure(text=f"✓  {label}", text_color=COLORS["success"])
            else:
                row.configure(text=f"○  {label}", text_color=COLORS["text_secondary"])


# ==========================================================================
# TOAST / PROFESSIONAL POPUP MESSAGE
# ==========================================================================
class Toast(ctk.CTkFrame):
    """A slide-down, auto-dismissing notification banner (success/error/warning)."""

    def __init__(self, master, message, kind="success", duration_ms=3200):
        color_map = {
            "success": COLORS["success"],
            "error": COLORS["error"],
            "warning": COLORS["warning"],
            "info": COLORS["primary"],
        }
        icon_map = {"success": "✓", "error": "✕", "warning": "!", "info": "i"}
        color = color_map.get(kind, COLORS["primary"])

        super().__init__(master, fg_color=COLORS["card"], corner_radius=RADIUS["input"],
                          border_width=1.5, border_color=color)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=14, pady=10)

        badge = ctk.CTkLabel(
            inner, text=icon_map.get(kind, "i"), width=22, height=22,
            fg_color=color, text_color=COLORS["white"], corner_radius=11,
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1], weight="bold")
        )
        badge.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            inner, text=message, font=ctk.CTkFont(*FONTS["body"]),
            text_color=COLORS["text"], wraplength=280, justify="left"
        ).pack(side="left")

        self.place(relx=0.5, rely=-0.1, anchor="n")
        Animator.tween(self, -0.1, 0.04, 400, lambda v: self.place_configure(rely=v))
        self.after(duration_ms, self._dismiss)

    def _dismiss(self):
        Animator.tween(self, 0.04, -0.15, 350, lambda v: self.place_configure(rely=v),
                        on_done=self.destroy)
