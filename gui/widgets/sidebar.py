import customtkinter as ctk
from gui.config import FONT_SUBTITLE, FONT_NORMAL, DEFAULT_PARAMS


class SidebarFrame(ctk.CTkFrame):
    """Lewy panel z parametrami"""
    
    def __init__(self, parent, on_instance_load=None, on_optimize=None, **kwargs):
        super().__init__(parent, fg_color="#161b22", corner_radius=12, **kwargs)
        
        self.on_instance_load = on_instance_load
        self.instance_loaded = False
        
        # === GÓRNY PANEL: Ze scrollem (Instance + GA Params) ===
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#161b22",
            scrollbar_button_color="#30363d",
            scrollbar_button_hover_color="#484f58"
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0, side="top")
        
        # --- Sekcja: Instancja ---
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
        
        # self.instance_info = ctk.CTkLabel(
        #     self.scrollable_frame,
        #     text="No instance loaded",
        #     text_color="#8b949e",
        #     font=("Segoe UI", 9)
        # )
        # self.instance_info.pack(anchor="w", pady=5)
        
        # Separator
        self._create_separator()
        
        # --- Sekcja: Parametry GA ---
        self._create_section("GA Parameters")
        
        self.params = {}
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
        
        # Seed osobno
        seed_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Random Seed (0=random):",
            text_color="#ffffff"
        )
        seed_label.pack(anchor="w", pady=(8, 2))
        
        self.params["seed"] = ctk.CTkEntry(
            self.scrollable_frame,
            fg_color="#0d1117",
            border_color="#30363d",
            text_color="#ffffff"
        )
        self.params["seed"].insert(0, str(DEFAULT_PARAMS["seed"]))
        self.params["seed"].pack(fill="x", pady=(0, 10))
    
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
    
    def _on_browse(self):
        """Callback gdy kliknięty Browse"""
        if self.on_instance_load:
            result = self.on_instance_load()
            if result:
                file_path, jobs, machines = result
                self.instance_file.delete(0, "end")
                self.instance_file.insert(0, file_path)
                self.instance_info.configure(text=f"{jobs} jobs, {machines} machines")
                self.instance_loaded = True
    
    def get_parameters(self):
        """Zwróć wszystkie parametry"""
        params = {}
        for key, entry in self.params.items():
            try:
                if key in ["population_size", "generations", "tournament_size", "seed"]:
                    params[key] = int(entry.get())
                else:
                    params[key] = float(entry.get())
            except ValueError:
                return None
        return params
