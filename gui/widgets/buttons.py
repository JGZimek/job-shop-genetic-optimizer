import customtkinter as ctk

class ButtonsFrame(ctk.CTkFrame):
    """
    Dolny panel z przyciskami akcji.
    Zoptymalizowany pod kątem spójności z kompaktowym Sidebarem.
    """
    
    def __init__(self, parent, on_optimize=None, on_clear=None, on_export=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_optimize = on_optimize
        self.on_clear = on_clear
        self.on_export = on_export
        
        # Inner frame dla marginesów
        # Zmniejszony pady z 15 na 10, aby pasował do Sidebaru
        inner = ctk.CTkFrame(self, fg_color="#161b22")
        inner.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Run Optimization Button (Najważniejszy - lekko większy)
        self.optimize_btn = ctk.CTkButton(
            inner,
            text="Run Optimization",
            command=self._on_optimize_click,
            fg_color="#238636",
            hover_color="#2ea043",
            height=36,  # Zoptymalizowana wysokość
            font=("Segoe UI", 12, "bold")
        )
        self.optimize_btn.pack(fill="x", pady=(0, 6)) # Mniejszy odstęp
        self.optimize_btn.configure(state="disabled")
        
        # Export Button
        self.export_btn = ctk.CTkButton(
            inner,
            text="Export Schedule",
            command=self._on_export_click,
            fg_color="#0078ff",
            hover_color="#0066cc",
            height=32,  # Standardowa wysokość (jak w Sidebar)
            font=("Segoe UI", 11, "bold")
        )
        self.export_btn.pack(fill="x", pady=(0, 6)) # Mniejszy odstęp
        self.export_btn.configure(state="disabled")
        
        # Clear Results Button
        self.clear_btn = ctk.CTkButton(
            inner,
            text="Clear Results",
            command=self._on_clear_click,
            fg_color="#da3633",
            hover_color="#f85149",
            height=32,
            font=("Segoe UI", 11, "bold")
        )
        self.clear_btn.pack(fill="x")
    
    def _on_optimize_click(self):
        """Handle optimize button click"""
        if self.on_optimize:
            self.on_optimize()
    
    def _on_export_click(self):
        """Handle export button click"""
        if self.on_export:
            self.on_export()
    
    def _on_clear_click(self):
        """Handle clear button click"""
        if self.on_clear:
            self.on_clear()
    
    def enable_optimize(self):
        """Enable optimize button"""
        self.optimize_btn.configure(state="normal")
    
    def disable_optimize(self):
        """Disable optimize button"""
        self.optimize_btn.configure(state="disabled")
    
    def enable_export(self):
        """Enable export button"""
        self.export_btn.configure(state="normal")
    
    def disable_export(self):
        """Disable export button"""
        self.export_btn.configure(state="disabled")