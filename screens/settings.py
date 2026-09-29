import tkinter as tk
from tkinter import ttk
from .base_screen import BaseScreen


class SettingsScreen(BaseScreen):
    title="הגדרות"

    def __init__(self,parent,navigate=None,get_reservations_visible=None,
                 toggle_reservations=None,get_console_visible=None,
                 toggle_console=None,save_setup=None,restore_setup=None):
        self.get_reservations_visible=get_reservations_visible
        self.toggle_reservations_action=toggle_reservations
        self.get_console_visible=get_console_visible
        self.toggle_console_action=toggle_console
        self.save_setup_action=save_setup
        self.restore_setup_action=restore_setup
        self.initial_reservations_visible=get_reservations_visible()
        self.initial_console_visible=get_console_visible()
        super().__init__(parent,navigate)
        self.build()

    def build(self):
        panel=tk.LabelFrame(self,text="הגדרות תצוגה",bg="#f3f4f6",labelanchor="ne")
        panel.pack(fill="x",padx=35,pady=25)
        panel.grid_anchor("e")

        self.reservations_button=ttk.Button(panel,command=self.toggle_reservations)
        self.reservations_button.grid(row=0,column=0,padx=12,pady=12,sticky="e")

        self.console_button=ttk.Button(panel,command=self.toggle_console)
        self.console_button.grid(row=1,column=0,padx=12,pady=12,sticky="e")
        ttk.Button(panel,text="שמור מצב",command=self.save_setup).grid(
            row=2,column=0,padx=12,pady=12,sticky="e")
        ttk.Button(panel,text="חזור למצב ראשוני",command=self.go_back).grid(
            row=3,column=0,padx=12,pady=12,sticky="e")
        self.refresh_labels()

    def refresh_labels(self):
        reservations_visible=self.get_reservations_visible()
        self.reservations_button.config(
            text="הסתר כפתור הזמנות" if reservations_visible else "הצג כפתור הזמנות")
        console_visible=self.get_console_visible()
        self.console_button.config(
            text="הסתר מסוף" if console_visible else "הצג מסוף")

    def toggle_reservations(self):
        self.toggle_reservations_action()
        self.refresh_labels()

    def toggle_console(self):
        self.toggle_console_action()
        self.refresh_labels()

    def save_setup(self):
        self.save_setup_action()

    def go_back(self):
        self.restore_setup_action(False,False)
        self.refresh_labels()
