import customtkinter as ctk

# --- KONFIGURACJA KOLORÓW ---
COLOR_ERROR = "#cf222e"     # Czerwony
COLOR_WARNING = "#d29922"   # Bursztynowy
COLOR_SUCCESS = "#238636"   # Zielony
COLOR_INFO = "#0078ff"      # Niebieski
COLOR_NORMAL = "#30363d"    # Szary
COLOR_BG_DARK = "#1c2128"   # Tło okna
COLOR_BG_LIGHT = "#0d1117"  # Tło detali

class StatusDialog(ctk.CTkToplevel):
    """
    Uniwersalne okno powiadomień.
    Dla type_='warning' wyświetla Cancel/Continue i zwraca self.result.
    """
    def __init__(self, parent, title, message, details=None, type_="error"):
        super().__init__(parent)
        
        self.result = False  # Domyślnie False (Cancel/Close)
        self.type_ = type_
        
        # 1. Konfiguracja w zależności od typu
        if type_ == "error":
            self.main_color = COLOR_ERROR
            self.btn_text = "OK"
            self.show_cancel = False
        elif type_ == "warning":
            self.main_color = COLOR_WARNING
            self.btn_text = "Continue Anyway" # Tekst przycisku akceptacji
            self.show_cancel = True           # Włączamy przycisk anulowania
        elif type_ == "success":
            self.main_color = COLOR_SUCCESS
            self.btn_text = "OK"
            self.show_cancel = False
        else: # info
            self.main_color = COLOR_INFO
            self.btn_text = "OK"
            self.show_cancel = False

        self.title(title)
        
        # Wysokość okna
        h = 360 if details else 220
        self.geometry(f"420x{h}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=COLOR_BG_DARK)
        
        # --- UKŁAD OKNA ---
        
        # 2. Ramka przycisków (Packujemy najpierw z side="bottom", żeby były zawsze na dole)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=20, padx=25)
        
        # Logika przycisków
        if self.show_cancel:
            # Przycisk Cancel (lewa strona)
            ctk.CTkButton(
                btn_frame, 
                text="Cancel", 
                fg_color="transparent", 
                border_width=1, 
                border_color=COLOR_NORMAL,
                text_color="#e6edf3",
                hover_color=COLOR_NORMAL, 
                width=100, 
                command=self._on_cancel
            ).pack(side="left")
            
            # Przycisk Continue (prawa strona)
            ctk.CTkButton(
                btn_frame, 
                text=self.btn_text, 
                fg_color=COLOR_BG_LIGHT, 
                border_width=1, 
                border_color=self.main_color,
                text_color=self.main_color, 
                hover_color=COLOR_NORMAL, 
                width=140, 
                command=self._on_confirm
            ).pack(side="right")
        else:
            # Pojedynczy przycisk OK
            ctk.CTkButton(
                btn_frame, 
                text=self.btn_text, 
                fg_color=self.main_color, 
                hover_color=COLOR_NORMAL, 
                width=100, 
                command=self._on_confirm
            ).pack(side="right")

        # 3. Treść (Packujemy resztę)
        
        # Nagłówek
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame, 
            text=title, 
            font=("Segoe UI", 19, "bold"), 
            text_color=self.main_color
        ).pack()
        
        # Wiadomość
        ctk.CTkLabel(
            self, 
            text=message, 
            font=("Segoe UI", 13), 
            wraplength=380, 
            text_color="#e6edf3",
            justify="center"
        ).pack(pady=(0, 10), padx=20)
        
        # Detale (opcjonalne)
        if details:
            details_frame = ctk.CTkScrollableFrame(
                self, fg_color=COLOR_BG_LIGHT, 
                border_color=self.main_color, border_width=1, corner_radius=6
            )
            # fill="both" i expand=True pozwoli zająć dostępną przestrzeń między nagłówkiem a przyciskami
            details_frame.pack(fill="both", expand=True, padx=25, pady=(0, 10))
            
            ctk.CTkLabel(
                details_frame, 
                text=details, 
                font=("Consolas", 12), 
                text_color=self.main_color, 
                justify="left",
                wraplength=320,
                anchor="w"
            ).pack(anchor="w", padx=5, pady=5, fill="x")

        # Wyśrodkowanie okna na ekranie (po zbudowaniu UI)
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
            self.geometry(f"+{x}+{y}")
        except:
            pass 

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window() # WAŻNE: Czeka aż okno zostanie zamknięte

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()