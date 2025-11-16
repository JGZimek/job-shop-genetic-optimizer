import customtkinter as ctk
from gui.config import FONT_SUBTITLE, FONT_NORMAL, DEFAULT_PARAMS


class SidebarFrame(ctk.CTkFrame):
    """Lewy panel z parametrami"""
    
    def __init__(self, parent, on_instance_load=None, on_algorithm_change=None, **kwargs):
        super().__init__(parent, fg_color="#161b22", corner_radius=12, **kwargs)
        
        self.on_instance_load = on_instance_load
        self.on_algorithm_change_callback = on_algorithm_change
        self.instance_loaded = False
        self.selected_algorithm = "genetic"
        
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#161b22",
            scrollbar_button_color="#30363d",
            scrollbar_button_hover_color="#484f58"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0, side="top")
        
        # --- Instance ---
        self._create_section("Load Instance")
        
        self.instance_file = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="No file selected",
            fg_color="#0d1117",
            border_color="#30363d",
            text_color="#ffffff"
        )
        self.instance_file.pack(fill="x", pady=5)
        
        self.browse_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="Browse Files",
            command=self._on_browse,
            fg_color="#0078ff",
            hover_color="#0066cc"
        )
        self.browse_btn.pack(fill="x", pady=5)
        
        self._create_separator()
        
        # --- Algorithm Selection ---
        self._create_section("Algorithm")
        
        self.algorithm_dropdown = ctk.CTkOptionMenu(
            self.scrollable_frame,
            values=["Genetic", "Greedy", "Exact (A*)"],
            command=self._on_algorithm_change,
            fg_color="#0078ff",
            button_color="#0066cc",
            button_hover_color="#0055aa",
            text_color="#ffffff"
        )
        self.algorithm_dropdown.set("Genetic")
        self.algorithm_dropdown.pack(fill="x", pady=5)
        
        self._create_separator()
        
        # --- GA Parameters Section ---
        self.ga_section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="GA Parameters",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        )
        self.ga_section_label.pack(anchor="w", pady=(15, 10))
        
        self.params = {}
        self.param_labels = {}
        self.param_entries = {}
        
        for param_name, default_value in DEFAULT_PARAMS.items():
            if param_name != "seed":
                display_name = param_name.replace("_", " ").title()
                
                label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=f"{display_name}:",
                    text_color="#ffffff"
                )
                label.pack(anchor="w", pady=(8, 2))
                
                entry = ctk.CTkEntry(
                    self.scrollable_frame,
                    fg_color="#0d1117",
                    border_color="#30363d",
                    text_color="#ffffff"
                )
                entry.insert(0, str(default_value))
                entry.pack(fill="x", pady=(0, 10))
                
                self.params[param_name] = entry
                self.param_labels[param_name] = label
                self.param_entries[param_name] = entry
        
        # Seed
        seed_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Random Seed (0=random):",
            text_color="#ffffff"
        )
        seed_label.pack(anchor="w", pady=(8, 2))
        
        seed_entry = ctk.CTkEntry(
            self.scrollable_frame,
            fg_color="#0d1117",
            border_color="#30363d",
            text_color="#ffffff"
        )
        seed_entry.insert(0, str(DEFAULT_PARAMS["seed"]))
        seed_entry.pack(fill="x", pady=(0, 10))
        
        self.params["seed"] = seed_entry
        self.param_labels["seed"] = seed_label
        self.param_entries["seed"] = seed_entry
        
        # --- Greedy Info Section ---
        self.greedy_info_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Greedy Algorithm",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        )
        
        self.greedy_info = ctk.CTkLabel(
            self.scrollable_frame,
            text="Fast heuristic approach. Suitable for all instance sizes. Provides approximate solution.",
            text_color="#8b949e",
            font=("Segoe UI", 11),
            wraplength=200,
            justify="left"
        )
        
        # --- Exact Info Section ---
        self.exact_section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Exact Algorithm (A*)",
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        )
        
        self.exact_warning = ctk.CTkLabel(
            self.scrollable_frame,
            text="Not recommended for instances larger than 4x3 (4 jobs, 3 machines). Due to high computational complexity, solving larger instances may take extremely long or require excessive memory.",
            text_color="#ff9800",
            font=("Segoe UI", 11),
            wraplength=200,
            justify="left"
        )
        
        self.exact_info = ctk.CTkLabel(
            self.scrollable_frame,
            text="Guaranteed optimal solution. A* search with admissible heuristic.",
            text_color="#8b949e",
            font=("Segoe UI", 11),
            wraplength=200,
            justify="left"
        )
        
        # Initialize visibility (defaultowo genetic)
        self._update_param_visibility()
    
    def _create_section(self, title):
        """Utwórz sekcję z tytułem"""
        section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff"
        )
        section_label.pack(anchor="w", pady=(15, 10))
    
    def _create_separator(self):
        """Utwórz separator"""
        separator = ctk.CTkFrame(
            self.scrollable_frame,
            height=1,
            fg_color="#30363d"
        )
        separator.pack(fill="x", pady=15)
    
    def _on_algorithm_change(self, choice):
        """Zmiana algorytmu"""
        if choice == "Genetic":
            self.selected_algorithm = "genetic"
        elif choice == "Greedy":
            self.selected_algorithm = "greedy"
        elif choice == "Exact (A*)":
            self.selected_algorithm = "exact"
        
        self._update_param_visibility()
    
    def _update_param_visibility(self):
        """Pokaż/ukryj parametry i wskazówki w zależności od algorytmu"""
        ga_params = ["population_size", "generations", "tournament_size", "mutation_prob", "seed"]
        
        if self.selected_algorithm == "genetic":
            # Pokaż GA sekcję
            self.ga_section_label.pack(anchor="w", pady=(15, 10))
            for param in ga_params:
                self.param_labels[param].pack(anchor="w", pady=(8, 2))
                self.param_entries[param].pack(fill="x", pady=(0, 10))
            
            # Ukryj inne
            self.greedy_info_label.pack_forget()
            self.greedy_info.pack_forget()
            self.exact_section_label.pack_forget()
            self.exact_warning.pack_forget()
            self.exact_info.pack_forget()
        
        elif self.selected_algorithm == "greedy":
            # Ukryj GA sekcję
            self.ga_section_label.pack_forget()
            for param in ga_params:
                self.param_labels[param].pack_forget()
                self.param_entries[param].pack_forget()
            
            # Pokaż Greedy info
            self.greedy_info_label.pack(anchor="w", pady=(15, 10))
            self.greedy_info.pack(anchor="w", pady=10)
            
            # Ukryj Exact
            self.exact_section_label.pack_forget()
            self.exact_warning.pack_forget()
            self.exact_info.pack_forget()
        
        elif self.selected_algorithm == "exact":
            # Ukryj GA sekcję
            self.ga_section_label.pack_forget()
            for param in ga_params:
                self.param_labels[param].pack_forget()
                self.param_entries[param].pack_forget()
            
            # Ukryj Greedy
            self.greedy_info_label.pack_forget()
            self.greedy_info.pack_forget()
            
            # Pokaż Exact
            self.exact_section_label.pack(anchor="w", pady=(15, 10))
            self.exact_warning.pack(anchor="w", pady=10)
            self.exact_info.pack(anchor="w", pady=10)
    
    def _on_browse(self):
        """Callback gdy kliknięty Browse"""
        if self.on_instance_load:
            result = self.on_instance_load()
            if result:
                file_path, jobs, machines = result
                self.instance_file.delete(0, "end")
                self.instance_file.insert(0, file_path)
                self.instance_loaded = True
    
    def get_parameters(self):
        """Zwróć wszystkie parametry"""
        algorithm = self.selected_algorithm
        
        if algorithm == "genetic":
            params = {"algorithm": "genetic"}
            for key, entry in self.params.items():
                try:
                    if key in ["population_size", "generations", "tournament_size", "seed"]:
                        params[key] = int(entry.get())
                    else:
                        params[key] = float(entry.get())
                except ValueError:
                    return None
            return params
        elif algorithm == "greedy":
            return {"algorithm": "greedy"}
        elif algorithm == "exact":
            return {"algorithm": "exact"}
        
        return None
    
    def get_algorithm(self):
        """Zwróć wybrany algorytm"""
        return self.selected_algorithm
