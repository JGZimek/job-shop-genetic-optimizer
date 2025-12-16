import customtkinter as ctk
from gui.config import DEFAULT_PARAMS
# Importujemy StatusDialog i kolory z zewnętrznego pliku, 
# aby zachować spójność z resztą aplikacji (np. exportem w main.py)
from gui.dialogs.status_dialog import StatusDialog, COLOR_ERROR, COLOR_WARNING, COLOR_NORMAL

class SidebarFrame(ctk.CTkFrame):
    """
    Panel boczny MAX ROBUST.
    Zapewnia walidację danych, obsługę błędów krytycznych i ostrzeżeń wydajnościowych.
    """
    
    def __init__(self, parent, on_instance_load=None, on_algorithm_change=None, **kwargs):
        super().__init__(parent, fg_color="#161b22", corner_radius=12, **kwargs)
        
        self.on_instance_load = on_instance_load
        self.on_algorithm_change_callback = on_algorithm_change
        self.instance_loaded = False
        self.selected_algorithm = "genetic"
        
        # --- 1. HARD LIMITS (Błędy Techniczne) ---
        # Przekroczenie tych wartości uniemożliwia uruchomienie algorytmu (blokada).
        self.constraints = {
            "population_size": {"type": int, "min": 10, "max": 1_000_000},
            "generations":     {"type": int, "min": 1, "max": 1_000_000},
            "tournament_size": {"type": int, "min": 1, "max": None}, 
            "mutation_prob":   {"type": float, "min": 0.0, "max": 1.0},
            "seed":            {"type": int, "min": 0, "max": 4294967295} # uint32 max
        }

        # --- 2. SOFT LIMITS (Ostrzeżenia Wydajności) ---
        # Przekroczenie tych wartości wyświetla ostrzeżenie, ale pozwala kontynuować.
        self.soft_limits = {
            "population_size": 5000, 
            "generations":     10000,
            "tournament_size": 500
        }

        # --- UI START ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#161b22")
        self.scrollable_frame.pack(fill="both", expand=True, side="top")
        
        self._setup_file_section()
        self._setup_algo_section()
        
        # Kontener na parametry genetyczne
        self.ga_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        ctk.CTkLabel(self.ga_container, text="GA Parameters", font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(0, 10))
        
        self.params_widgets = {}
        for param in ["population_size", "generations", "tournament_size", "mutation_prob", "seed"]:
            self._create_param_field(param)

        # Kontenery informacyjne (Greedy / Exact)
        self.greedy_container = self._create_info_container("Greedy Algorithm", "Fast heuristic approach.", "white")
        self.exact_container = self._create_info_container("Exact Algorithm (A*)", "Guaranteed optimal solution.", "white")
        ctk.CTkLabel(self.exact_container, text="⚠️ Only for small instances (< 4x4).", text_color=COLOR_WARNING, font=("Segoe UI", 11)).pack(anchor="w")

        self._update_param_visibility()

    def _create_param_field(self, param_key):
        """Tworzy pole edycyjne z etykietą i bindingiem walidacji"""
        display_name = param_key.replace("_", " ").title()
        if param_key == "seed": display_name = "Random Seed (0=Random)"
        
        frame = ctk.CTkFrame(self.ga_container, fg_color="transparent")
        frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(frame, text=f"{display_name}:", text_color="white").pack(anchor="w", pady=(5, 2))
        
        entry = ctk.CTkEntry(frame, fg_color="#0d1117", border_color=COLOR_NORMAL, text_color="white")
        entry.insert(0, str(DEFAULT_PARAMS.get(param_key, 0)))
        entry.pack(fill="x", pady=(0, 5))
        
        # Live feedback: Walidacja kolorystyczna przy opuszczeniu pola lub wciśnięciu Enter
        entry.bind("<FocusOut>", lambda e, k=param_key: self._validate_field_live(k))
        entry.bind("<Return>", lambda e, k=param_key: self._validate_field_live(k))
        
        self.params_widgets[param_key] = entry

    def _validate_field_live(self, key):
        """
        Szybka walidacja wizualna (zmienia tylko kolory ramki).
        Nie blokuje UI, daje natychmiastowy feedback.
        """
        entry = self.params_widgets.get(key)
        raw_val = entry.get().strip()
        constraint = self.constraints.get(key)
        
        # Jeśli puste, ignoruj (get_parameters wyłapie to później jako błąd)
        if not raw_val: return 
        
        try:
            # Konwersja (obsługa kropki i przecinka)
            val = int(raw_val) if constraint["type"] is int else float(raw_val.replace(",", "."))
            
            # 1. Sprawdzenie Błędu (Czerwony)
            if (constraint["min"] is not None and val < constraint["min"]) or \
               (constraint["max"] is not None and val > constraint["max"]):
                entry.configure(border_color=COLOR_ERROR)
                return

            # 2. Sprawdzenie Ostrzeżenia (Pomarańczowy)
            soft_limit = self.soft_limits.get(key)
            if soft_limit and val > soft_limit:
                entry.configure(border_color=COLOR_WARNING)
            else:
                entry.configure(border_color=COLOR_NORMAL) # OK (Szary)

        except ValueError:
            entry.configure(border_color=COLOR_ERROR)

    def get_parameters(self):
        """
        Główna metoda pobierania parametrów.
        Zwraca słownik parametrów LUB None.
        Obsługuje WSZYSTKIE komunikaty (Błędy i Ostrzeżenia) używając StatusDialog.
        """
        # Dla algorytmów bez parametrów od razu zwracamy wynik
        if self.selected_algorithm != "genetic":
            return {"algorithm": self.selected_algorithm}

        clean_params = {"algorithm": "genetic"}
        errors_list = []
        warnings_list = []
        
        # 1. Iteracja po wszystkich polach i walidacja
        for key, widget in self.params_widgets.items():
            raw_val = widget.get().strip()
            constraint = self.constraints[key]
            nice_name = key.replace("_", " ").title()

            try:
                if not raw_val: raise ValueError("Field cannot be empty")
                
                # Konwersja typów
                if constraint["type"] is int:
                    val = int(raw_val)
                else:
                    val = float(raw_val.replace(",", "."))

                # Sprawdzenie Hard Limits (Błędy krytyczne)
                if constraint["min"] is not None and val < constraint["min"]:
                    raise ValueError(f"Value too small (min: {constraint['min']})")
                if constraint["max"] is not None and val > constraint["max"]:
                    raise ValueError(f"Value too large (max: {constraint['max']})")

                clean_params[key] = val
                
                # Sprawdzenie Soft Limits (Ostrzeżenia wydajności)
                soft_limit = self.soft_limits.get(key)
                if soft_limit and val > soft_limit:
                    warnings_list.append(f"• {nice_name}: {val}\n  (Recommended max: {soft_limit})")

            except ValueError as e:
                # Formatowanie komunikatu błędu
                msg = str(e).replace('invalid literal for int() with base 10:', 'Must be a valid number')
                errors_list.append(f"• {nice_name}: {msg}")
                widget.configure(border_color=COLOR_ERROR)

        # 2. Walidacja logiczna (zależności między parametrami)
        if "population_size" in clean_params and "tournament_size" in clean_params:
            if clean_params["tournament_size"] > clean_params["population_size"]:
                errors_list.append("• Tournament Size: Cannot be larger than Population Size")
                self.params_widgets["tournament_size"].configure(border_color=COLOR_ERROR)

        # 3. Wyświetlanie Okien Dialogowych (Priorytet: Błędy -> Ostrzeżenia -> Sukces)
        
        # SCENARIUSZ A: Błędy Krytyczne -> Blokujemy start
        if errors_list:
            StatusDialog(
                self.winfo_toplevel(),
                title="Configuration Error",
                message="Please fix the following errors before starting the algorithm:",
                details="\n".join(errors_list),
                type_="error"
            )
            return None # Zwracamy None, main.py nie uruchomi wątku

        # SCENARIUSZ B: Ostrzeżenia -> Pytamy użytkownika
        if warnings_list:
            dialog = StatusDialog(
                self.winfo_toplevel(),
                title="Performance Warning",
                message="The parameters you entered are unusually high. This may cause the algorithm to run for a very long time.",
                details="\n".join(warnings_list),
                type_="warning"
            )
            
            # Jeśli użytkownik kliknie "Cancel", przerywamy
            if not dialog.result:
                return None 
        
        # SCENARIUSZ C: Wszystko OK (lub użytkownik zaakceptował ryzyko)
        return clean_params

    # --- Metody pomocnicze UI (bez zmian logicznych) ---
    def _setup_file_section(self):
        self._create_section("Load Instance")
        self.instance_file = ctk.CTkEntry(self.scrollable_frame, placeholder_text="No file", fg_color="#0d1117", state="readonly")
        self.instance_file.pack(fill="x", pady=5)
        ctk.CTkButton(self.scrollable_frame, text="Browse Files", command=self._on_browse).pack(fill="x", pady=5)
        self._create_separator()

    def _setup_algo_section(self):
        self._create_section("Algorithm")
        self.algorithm_dropdown = ctk.CTkOptionMenu(self.scrollable_frame, values=["Genetic", "Greedy", "Exact (A*)"], command=self._on_algorithm_change)
        self.algorithm_dropdown.set("Genetic")
        self.algorithm_dropdown.pack(fill="x", pady=5)
        self._create_separator()
        
    def _create_section(self, title):
        ctk.CTkLabel(self.scrollable_frame, text=title, font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(15, 10))
    
    def _create_separator(self):
        ctk.CTkFrame(self.scrollable_frame, height=1, fg_color=COLOR_NORMAL).pack(fill="x", pady=15)
        
    def _create_info_container(self, title, desc, col):
        f = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(f, text=desc, text_color=col, font=("Segoe UI", 11), wraplength=200, justify="left").pack(anchor="w")
        return f
        
    def _on_algorithm_change(self, choice):
        self.selected_algorithm = {"Genetic": "genetic", "Greedy": "greedy", "Exact (A*)": "exact"}.get(choice, "genetic")
        self._update_param_visibility()
        if self.on_algorithm_change_callback: self.on_algorithm_change_callback(self.selected_algorithm)
        
    def _update_param_visibility(self):
        self.ga_container.pack_forget(); self.greedy_container.pack_forget(); self.exact_container.pack_forget()
        if self.selected_algorithm == "genetic": self.ga_container.pack(fill="x")
        elif self.selected_algorithm == "greedy": self.greedy_container.pack(fill="x")
        elif self.selected_algorithm == "exact": self.exact_container.pack(fill="x")
        
    def _on_browse(self):
        if self.on_instance_load:
            res = self.on_instance_load()
            if res:
                self.instance_file.configure(state="normal"); self.instance_file.delete(0, "end"); self.instance_file.insert(0, res[0]); self.instance_file.configure(state="readonly"); self.instance_loaded = True

    def get_algorithm(self): return self.selected_algorithm