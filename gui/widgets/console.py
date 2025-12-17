import customtkinter as ctk
from datetime import datetime

# Paleta kolorów (Minimalistyczna)
COLOR_TIMESTAMP = "#505050"  # Bardzo ciemny szary
COLOR_TEXT = "#c9d1d9"       # Standardowy tekst
COLOR_SUCCESS = "#3fb950"    # Zielony
COLOR_WARNING = "#d29922"    # Pomarańczowy
COLOR_ERROR = "#f85149"      # Czerwony
COLOR_ACCENT = "#58a6ff"     # Niebieski
COLOR_VALUE = "#a5d6ff"      # Jasnoniebieski

class ConsoleFrame(ctk.CTkFrame):
    """
    Konsola z logami - Wersja Compact & Crash-Free.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Tytuł - zmniejszony padding
        title_label = ctk.CTkLabel(
            self,
            text="Activity Logs",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w", pady=(0, 2), padx=5)
        
        # Textbox
        self.textbox = ctk.CTkTextbox(
            self, 
            font=("Consolas", 11), # Mniejsza czcionka bazowa dla całej konsoli
            fg_color="#0d1117",
            text_color=COLOR_TEXT,
            activate_scrollbars=True,
            wrap="word" # Zawijanie słów
        )
        self.textbox.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Konfiguracja tagów (USUNIĘTO parametr 'font' który powodował błąd)
        self.textbox.tag_config("timestamp", foreground=COLOR_TIMESTAMP)
        self.textbox.tag_config("normal", foreground=COLOR_TEXT)
        self.textbox.tag_config("success", foreground=COLOR_SUCCESS)
        self.textbox.tag_config("warning", foreground=COLOR_WARNING)
        self.textbox.tag_config("error", foreground=COLOR_ERROR)
        self.textbox.tag_config("header", foreground=COLOR_ACCENT) 
        self.textbox.tag_config("value", foreground=COLOR_VALUE)

        self.textbox.configure(state="disabled")

    def _write(self, text, tag="normal"):
        """Prywatna metoda do pisania"""
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text, tag)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def _write_ts(self):
        """Krótki timestamp"""
        ts = datetime.now().strftime("%H:%M:%S")
        self._write(f"[{ts}] ", "timestamp")

    # --- PUBLIC API (Compact) ---

    def log_loaded(self, filename, jobs, machines, baseline):
        """Log ładowania - Jedna linia"""
        self._write_ts()
        self._write(f"Loaded: {filename} ", "success")
        self._write(f"({jobs}J x {machines}M\n) ", "value")
        # self._write(f"| Base: {baseline}\n", "normal")

    def log_algorithm_selected(self, algorithm):
        pass 

    def log_ga_params(self, p):
        """Log parametrów - Jedna linia zamiast listy"""
        self._write_ts()
        self._write("GA Config: ", "header")
        # Skrócony zapis w jednej linii
        info = f"Pop={p['population_size']} Gen={p['generations']} Tour={p['tournament_size']} Mut={p['mutation_prob']:.2f} Seed={p['seed']}"
        self._write(f"{info}\n", "value")

    def log_running(self, algorithm):
        """Log startu"""
        self._write_ts()
        self._write(f"Started: {algorithm}...\n", "warning")

    def log_completed(self, makespan, elapsed_time):
        """Log wyniku - Jedna linia"""
        self._write_ts()
        self._write("Done: ", "success")
        self._write(f"Makespan={makespan} ", "header")
        self._write(f"({elapsed_time:.2f}s)\n", "normal")

    def log_error(self, error_msg):
        """Log błędu"""
        self._write_ts()
        self._write(f"ERROR: {error_msg}\n", "error")

    def insert_log(self, text, tag="normal"):
        """Dla exportu i innych"""
        # Ignoruj puste nowe linie, żeby oszczędzać miejsce
        if text.strip() == "": return
        
        self._write_ts()
        if "Exported" in text:
            self._write(text.strip() + "\n", "success")
        elif "error" in text.lower():
            self._write(text.strip() + "\n", "error")
        else:
            self._write(text.strip() + "\n", tag)

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")