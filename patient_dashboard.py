"""
patient_dashboard.py
---------------------
Temporary Patient Dashboard shown immediately after a successful login.

Its only job in this Authentication Module is to prove that
login -> session -> navigation -> logout all work end-to-end. The real
health-assessment / ML prediction UI will replace this placeholder in a
later development stage — nothing here should be mistaken for that.
"""

import customtkinter as ctk

from utils.theme import COLORS, FONTS, RADIUS
from components.custom_widgets import HeartbeatLogo, GradientButton


class PatientDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout, width=1180, height=760):
        super().__init__(master, fg_color=COLORS["bg"])
        self.user = user
        self.on_logout = on_logout
        self.width, self.height = width, height
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo = HeartbeatLogo(center, size=72)
        logo.pack()
        logo.start_pulse()

        badge = ctk.CTkLabel(
            center, text="✓", width=52, height=52, corner_radius=26,
            fg_color=COLORS["success"], text_color=COLORS["white"],
            font=ctk.CTkFont(size=22, weight="bold")
        )
        badge.pack(pady=(14, 18))

        ctk.CTkLabel(
            center, text=f"Welcome, {self.user['full_name']}",
            font=ctk.CTkFont(*FONTS["h1"]), text_color=COLORS["text"]
        ).pack()

        ctk.CTkLabel(
            center, text="Your HeartCare AI journey starts here.",
            font=ctk.CTkFont(*FONTS["subtitle"]), text_color=COLORS["primary"]
        ).pack(pady=(4, 22))

        info_card = ctk.CTkFrame(
            center, fg_color=COLORS["card"], corner_radius=RADIUS["card"],
            border_width=1, border_color=COLORS["border"]
        )
        info_card.pack(pady=(0, 26))

        inner = ctk.CTkFrame(info_card, fg_color="transparent")
        inner.pack(padx=32, pady=22)

        ctk.CTkLabel(
            inner, text="🩺", font=ctk.CTkFont(size=22)
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            inner,
            text="Patient health assessment will be available\nin the next module.",
            font=ctk.CTkFont(*FONTS["body"]), text_color=COLORS["text_secondary"],
            justify="center"
        ).pack()

        GradientButton(
            center, "Logout", command=self.on_logout, style="outline"
        ).pack()
