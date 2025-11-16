import customtkinter as ctk


class ConsoleFrame(ctk.CTkFrame):
    """Konsola z logami"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        title_label = ctk.CTkLabel(
            self,
            text="Logs",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        self.textbox = ctk.CTkTextbox(self)
        self.textbox.pack(fill="both", expand=True)
    
    def insert_log(self, text):
        """Wstaw log"""
        self.textbox.insert("end", text)
        self.textbox.see("end")
    
    def clear(self):
        """Wyczyść logi"""
        self.textbox.delete("1.0", "end")
