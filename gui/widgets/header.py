import customtkinter as ctk


class HeaderFrame(ctk.CTkFrame):
    """Górny pasek ze statusami i informacjami"""
    
    def __init__(self, parent, bindings_available=True, **kwargs):
        super().__init__(
            parent,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d",
            **kwargs
        )
        
        self.bindings_available = bindings_available
        
        # Lewo: Instance info
        self.instance_label = ctk.CTkLabel(
            self,
            text="No instance loaded",
            text_color="#8b949e",
            font=("Segoe UI", 12),
            fg_color="#161b22"
        )
        self.instance_label.pack(side="left", padx=15, pady=10)
        
        # Separator
        separator = ctk.CTkLabel(
            self,
            text="│",
            text_color="#30363d",
            font=("Segoe UI", 12),
            fg_color="#161b22"
        )
        separator.pack(side="left", padx=5)
        
        # Środek: Status/Wyniki
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            text_color="#8b949e",
            font=("Segoe UI", 12),
            fg_color="#161b22"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=10)
        
        # Separator
        separator2 = ctk.CTkLabel(
            self,
            text="│",
            text_color="#30363d",
            font=("Segoe UI", 12),
            fg_color="#161b22"
        )
        separator2.pack(side="left", padx=5)
        
        # Prawo: Status bindingów
        status_color = "#00ff00" if bindings_available else "#ff0000"
        status_text = "C++ Bindings Loaded" if bindings_available else "C++ Bindings Error"
        
        self.bindings_label = ctk.CTkLabel(
            self,
            text=status_text,
            text_color=status_color,
            font=("Segoe UI", 12),
            fg_color="#161b22"
        )
        self.bindings_label.pack(side="right", padx=15, pady=10)
    
    def set_instance_info(self, filename, jobs, machines):
        """Wyświetl info o wczytanej instancji"""
        self.instance_label.configure(
            text=f"{filename} | {jobs} jobs, {machines} machines",
            text_color="#ffffff"
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
