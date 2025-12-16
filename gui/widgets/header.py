import customtkinter as ctk

class HeaderFrame(ctk.CTkFrame):
    """
    Górny pasek ze statusami i informacjami.
    Zoptymalizowany: profesjonalne separatory i spójna paleta kolorów.
    """
    
    def __init__(self, parent, bindings_available=True, **kwargs):
        super().__init__(
            parent,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d",
            height=40, # Jawna wysokość pomaga w układzie
            **kwargs
        )
        
        self.bindings_available = bindings_available
        
        # --- LEWO: Instance info ---
        self.instance_label = ctk.CTkLabel(
            self,
            text="No instance loaded",
            text_color="#8b949e",
            font=("Segoe UI", 12),
            anchor="w"
        )
        self.instance_label.pack(side="left", padx=15, pady=8)
        
        # Separator 1 (Pionowa kreska jako Frame, nie tekst)
        self._create_separator()
        
        # --- ŚRODEK: Status/Wyniki ---
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            text_color="#8b949e",
            font=("Segoe UI", 12),
            anchor="center"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        # Separator 2
        self._create_separator()
        
        # --- PRAWO: Status bindingów ---
        # Używamy kolorów spójnych z konsolą (GitHub theme)
        status_color = "#3fb950" if bindings_available else "#f85149" # Stonowany zielony/czerwony
        status_text = "C++ Bindings Loaded" if bindings_available else "C++ Bindings Error"
        
        self.bindings_label = ctk.CTkLabel(
            self,
            text=status_text,
            text_color=status_color,
            font=("Segoe UI", 12, "bold"), # Pogrubienie dla ważnego statusu
            anchor="e"
        )
        self.bindings_label.pack(side="right", padx=15, pady=8)
    
    def _create_separator(self):
        """Tworzy estetyczny pionowy separator"""
        sep = ctk.CTkFrame(
            self, 
            width=2,           # Cienki pasek
            height=16,         # Wysokość mniejsza niż rodzica
            fg_color="#30363d",
            corner_radius=0
        )
        # pady kontroluje wysokość separatora wewnątrz paska
        sep.pack(side="left", padx=5, pady=10) 
    
    def set_instance_info(self, filename, jobs, machines):
        """Wyświetl info o wczytanej instancji"""
        self.instance_label.configure(
            text=f"{filename}  •  {jobs} Jobs  •  {machines} Machines", # Ładniejsze formatowanie
            text_color="#e6edf3" # Jaśniejszy kolor po załadowaniu
        )
    
    def update_status(self, text, color="#8b949e"):
        """Aktualizuj status"""
        self.status_label.configure(text=text, text_color=color)
    
    def reset_instance_info(self):
        """Reset info o instancji"""
        self.instance_label.configure(
            text="No instance loaded",
            text_color="#8b949e"
        )