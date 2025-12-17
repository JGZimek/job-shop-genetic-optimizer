import customtkinter as ctk
from gui.config import DEFAULT_PARAMS
from gui.dialogs.status_dialog import StatusDialog, COLOR_ERROR, COLOR_WARNING, COLOR_NORMAL

class SidebarFrame(ctk.CTkFrame):
    """
    Panel boczny OPTIMIZED & ROBUST.
    """
    
    def __init__(self, parent, on_instance_load=None, on_algorithm_change=None, **kwargs):
        super().__init__(parent, fg_color="#161b22", corner_radius=12, **kwargs)
        
        self.on_instance_load = on_instance_load
        self.on_algorithm_change_callback = on_algorithm_change
        self.instance_loaded = False
        self.selected_algorithm = "genetic"
        
        # Hard Limits
        self.constraints = {
            "population_size": {"type": int, "min": 10, "max": 1_000_000},
            "generations":     {"type": int, "min": 1, "max": 1_000_000},
            "tournament_size": {"type": int, "min": 1, "max": None}, 
            "mutation_prob":   {"type": float, "min": 0.0, "max": 1.0},
            "seed":            {"type": int, "min": 0, "max": 4294967295}
        }

        # Soft Limits
        self.soft_limits = {
            "population_size": 5000, 
            "generations":     10000,
            "tournament_size": 500
        }

        # Layout
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="#161b22",
            scrollbar_button_color="#30363d",
            scrollbar_button_hover_color="#484f58"
        )
        self.scrollable_frame.pack(fill="both", expand=True, side="top")
        
        self._setup_file_section()
        self._setup_algo_section()
        
        self.ga_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.ga_container.pack(fill="x", pady=0)
        
        ctk.CTkLabel(
            self.ga_container, text="GA Parameters", 
            font=("Segoe UI", 13, "bold"), text_color="white"
        ).pack(anchor="w", pady=(10, 5), padx=15)
        
        self.params_widgets = {}
        for param in ["population_size", "generations", "tournament_size", "mutation_prob", "seed"]:
            self._create_param_field(param)

        self._update_param_visibility()

    def _setup_file_section(self):
        ctk.CTkLabel(self.scrollable_frame, text="Load Instance", font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(15, 5), padx=15)
        self.instance_file = ctk.CTkEntry(self.scrollable_frame, placeholder_text="No file selected", fg_color="#0d1117", state="readonly", height=30, border_color="#30363d")
        self.instance_file.pack(fill="x", pady=3, padx=15)
        ctk.CTkButton(self.scrollable_frame, text="Browse Files", command=self._on_browse, height=30, fg_color="#238636", hover_color="#2ea043").pack(fill="x", pady=5, padx=15)
        ctk.CTkFrame(self.scrollable_frame, height=1, fg_color=COLOR_NORMAL).pack(fill="x", pady=15, padx=15)

    def _setup_algo_section(self):
        ctk.CTkLabel(self.scrollable_frame, text="Algorithm", font=("Segoe UI", 13, "bold"), text_color="white").pack(anchor="w", pady=(0, 5), padx=15)
        self.algorithm_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame, values=["Genetic", "Greedy", "Exact"], 
            command=self._on_algorithm_change, height=30, fg_color="#0078ff", button_color="#0066cc"
        )
        self.algorithm_dropdown.set("Genetic")
        self.algorithm_dropdown.pack(fill="x", pady=3, padx=15)
        
        self.exact_warning = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Warning: Not recommended for instances > 4x3. High complexity.", 
            text_color=COLOR_WARNING, font=("Segoe UI", 11), justify="left", wraplength=240, anchor="w"
        )
        self.algo_separator = ctk.CTkFrame(self.scrollable_frame, height=1, fg_color=COLOR_NORMAL)
        self.algo_separator.pack(fill="x", pady=15, padx=15)

    def _create_param_field(self, param_key):
        display = param_key.replace("_", " ").title()
        if param_key == "seed": display = "Random Seed (0=Random)"
        frame = ctk.CTkFrame(self.ga_container, fg_color="transparent")
        frame.pack(fill="x", pady=2, padx=15)
        ctk.CTkLabel(frame, text=f"{display}:", text_color="#b0b8c3", font=("Segoe UI", 11)).pack(anchor="w")
        entry = ctk.CTkEntry(frame, fg_color="#0d1117", border_color=COLOR_NORMAL, text_color="white", height=28)
        entry.insert(0, str(DEFAULT_PARAMS.get(param_key, 0)))
        entry.pack(fill="x", pady=(2, 5))
        
        entry.bind("<FocusOut>", lambda e, k=param_key: self._validate_field_live(k))
        entry.bind("<Return>", lambda e, k=param_key: self._validate_field_live(k))
        self.params_widgets[param_key] = entry

    def _update_param_visibility(self):
        self.ga_container.pack_forget()
        self.exact_warning.pack_forget()
        if self.selected_algorithm == "genetic":
            self.ga_container.pack(fill="x", pady=0)
        elif self.selected_algorithm == "exact":
            self.exact_warning.pack(in_=self.scrollable_frame, before=self.algo_separator, fill="x", pady=(5, 5), padx=20)

    def _on_algorithm_change(self, choice):
        self.selected_algorithm = {"Genetic": "genetic", "Greedy": "greedy", "Exact": "exact"}.get(choice, "genetic")
        self._update_param_visibility()
        if self.on_algorithm_change_callback: self.on_algorithm_change_callback(self.selected_algorithm)

    def _validate_field_live(self, key):
        entry = self.params_widgets.get(key)
        raw_val = entry.get().strip()
        constraint = self.constraints.get(key)
        if not raw_val: return 
        try:
            val = int(raw_val) if constraint["type"] is int else float(raw_val.replace(",", "."))
            if (constraint["min"] is not None and val < constraint["min"]) or \
               (constraint["max"] is not None and val > constraint["max"]):
                entry.configure(border_color=COLOR_ERROR)
            else:
                soft = self.soft_limits.get(key)
                entry.configure(border_color=COLOR_WARNING if soft and val > soft else COLOR_NORMAL)
        except ValueError:
            entry.configure(border_color=COLOR_ERROR)

    def get_parameters(self):
        if self.selected_algorithm != "genetic":
            return {"algorithm": self.selected_algorithm}

        clean_params = {"algorithm": "genetic"}
        errors_list = []
        warnings_list = []
        
        for key, widget in self.params_widgets.items():
            raw_val = widget.get().strip()
            constraint = self.constraints[key]
            nice_name = key.replace("_", " ").title()

            try:
                if not raw_val: raise ValueError("Required")
                val = int(raw_val) if constraint["type"] is int else float(raw_val.replace(",", "."))

                if constraint["min"] is not None and val < constraint["min"]: raise ValueError(f"Min: {constraint['min']}")
                if constraint["max"] is not None and val > constraint["max"]: raise ValueError(f"Max: {constraint['max']}")
                
                clean_params[key] = val
                
                soft_limit = self.soft_limits.get(key)
                if soft_limit and val > soft_limit:
                    warnings_list.append(f"• {nice_name}: {val} (High!)")

            except ValueError as e:
                errors_list.append(f"• {nice_name}: {str(e)}")
                widget.configure(border_color=COLOR_ERROR)

        if "population_size" in clean_params and "tournament_size" in clean_params:
            if clean_params["tournament_size"] > clean_params["population_size"]:
                errors_list.append("• Tournament Size > Population Size")
                self.params_widgets["tournament_size"].configure(border_color=COLOR_ERROR)

        # 1. Błędy (Blokujące - jeden przycisk OK)
        if errors_list:
            StatusDialog(self.winfo_toplevel(), "Configuration Error", "Please fix errors:", "\n".join(errors_list), type_="error")
            return None 

        # 2. Ostrzeżenia (Wybór - Cancel / Continue)
        if warnings_list:
            dialog = StatusDialog(
                self.winfo_toplevel(), 
                "Performance Warning", 
                "High complexity params detected.\nOptimization may take a long time.", 
                "\n".join(warnings_list), 
                type_="warning"
            )
            # Jeśli kliknięto Cancel, dialog.result będzie False
            if not dialog.result: 
                return None 
        
        return clean_params

    def _on_browse(self):
        if self.on_instance_load:
            res = self.on_instance_load()
            if res:
                self.instance_file.configure(state="normal"); self.instance_file.delete(0, "end"); self.instance_file.insert(0, res[0]); self.instance_file.configure(state="readonly"); self.instance_loaded = True

    def get_algorithm(self): return self.selected_algorithm