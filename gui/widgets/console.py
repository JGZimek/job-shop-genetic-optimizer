import customtkinter as ctk
from datetime import datetime


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
        
        self.textbox = ctk.CTkTextbox(self, font=("Courier", 11))
        self.textbox.pack(fill="both", expand=True)
        
        self.textbox.tag_config("info", foreground="#8b949e")
        self.textbox.tag_config("success", foreground="#00ff00")
        self.textbox.tag_config("warning", foreground="#ff9800")
        self.textbox.tag_config("error", foreground="#ff3333")
        self.textbox.tag_config("header", foreground="#0078ff")
    
    def insert_log(self, text, tag="info"):
        """Wstaw log"""
        self.textbox.insert("end", text, tag)
        self.textbox.see("end")
    
    def log_loaded(self, filename, jobs, machines, baseline):
        """Log załadowania instancji"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(f"Loaded: {filename} | {jobs}x{machines} | Baseline: {baseline}\n", "success")
    
    def log_algorithm_selected(self, algorithm):
        """Log wyboru algorytmu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(f"Algorithm: {algorithm}\n", "header")
    
    def log_ga_params(self, params):
        """Log parametrów GA"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(
            f"GA: pop={params['population_size']} gen={params['generations']} "
            f"tour={params['tournament_size']} mut={params['mutation_prob']} seed={params['seed']}\n",
            "header"
        )
    
    def log_running(self, algorithm):
        """Log uruchamiania"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(f"Running {algorithm}...\n", "warning")
    
    def log_completed(self, makespan, elapsed_time):
        """Log ukończenia"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(f"Completed: {elapsed_time:.2f}s | Makespan: {makespan}\n", "success")
        self.insert_log("\n", "info")
    
    def log_error(self, error_msg):
        """Log błędu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.insert_log(f"[{timestamp}] ", "info")
        self.insert_log(f"Error: {error_msg}\n", "error")
    
    def clear(self):
        """Wyczyść logi"""
        self.textbox.delete("1.0", "end")
