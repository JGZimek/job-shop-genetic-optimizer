import customtkinter as ctk

# --- KONFIGURACJA KOLORÓW ---
COLOR_ERROR = "#cf222e"     # Czerwony
COLOR_WARNING = "#d29922"   # Bursztynowy
COLOR_SUCCESS = "#238636"   # Zielony
COLOR_NORMAL = "#30363d"    # Szary
COLOR_BG_DARK = "#1c2128"   # Tło okna
COLOR_BG_LIGHT = "#0d1117"  # Tło detali

class StatusDialog(ctk.CTkToplevel):
    """
    Uniwersalne okno powiadomień (zastępuje messagebox).
    Type: 'error', 'warning', 'success', 'info'
    """
    def __init__(self, parent, title, message, details=None, type_="error"):
        super().__init__(parent)
        self.result = False
        self.type_ = type_
        
        # Konfiguracja stylu
        if type_ == "error":
            self.main_color = COLOR_ERROR
            icon = "❌"
            btn_text = "OK"
            self.is_confirmation = False
        elif type_ == "warning":
            self.main_color = COLOR_WARNING
            icon = "⚠️"
            btn_text = "Continue Anyway"
            self.is_confirmation = True
        elif type_ == "success":
            self.main_color = COLOR_SUCCESS
            icon = "✅"
            btn_text = "OK"
            self.is_confirmation = False
        else: # info
            self.main_color = "#0078ff"
            icon = "ℹ️"
            btn_text = "OK"
            self.is_confirmation = False

        self.title(title)
        # Dostosuj wysokość w zależności czy są detale
        h = 350 if details else 220
        self.geometry(f"420x{h}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Wyśrodkowanie
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
            self.geometry(f"+{x}+{y}")
        except:
            pass 

        self.configure(fg_color=COLOR_BG_DARK)
        
        # --- UI ---
        # Nagłówek
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text=icon, font=("Segoe UI", 24)).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text=title, font=("Segoe UI", 18, "bold"), text_color=self.main_color).pack(side="left")
        
        # Wiadomość główna
        ctk.CTkLabel(self, text=message, font=("Segoe UI", 13), wraplength=380, text_color="#e6edf3").pack(pady=5, padx=20)
        
        # Detale (np. lista wyeksportowanych plików lub treść błędu)
        if details:
            details_frame = ctk.CTkScrollableFrame(
                self, height=100, fg_color=COLOR_BG_LIGHT, 
                border_color=self.main_color, border_width=1, corner_radius=6
            )
            details_frame.pack(fill="both", expand=True, padx=25, pady=10)
            
            # --- POPRAWKA TUTAJ ---
            # Dodano wraplength=340, aby tekst łamał się wewnątrz ramki scrollowanej
            ctk.CTkLabel(
                details_frame, 
                text=details, 
                font=("Consolas", 12), 
                text_color=self.main_color, 
                justify="left",
                wraplength=340,  # <--- TO NAPRAWIA UCIĘTY TEKST
                anchor="w"
            ).pack(anchor="w", padx=5, pady=5, fill="x")
        
        # Przyciski
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=20, padx=25)
        
        if self.is_confirmation:
            ctk.CTkButton(
                btn_frame, text="Cancel", fg_color="transparent", border_width=1, border_color=COLOR_NORMAL,
                hover_color=COLOR_NORMAL, width=100, command=self._on_cancel
            ).pack(side="left")
            
            ctk.CTkButton(
                btn_frame, text=btn_text, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=self.main_color,
                text_color=self.main_color, hover_color=COLOR_NORMAL, width=140, command=self._on_confirm
            ).pack(side="right")
        else:
            ctk.CTkButton(
                btn_frame, text="OK", fg_color=self.main_color, hover_color=COLOR_NORMAL, 
                width=100, command=self._on_confirm
            ).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()