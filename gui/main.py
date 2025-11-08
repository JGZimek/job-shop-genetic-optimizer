import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

class JobShopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ustawienia okna
        self.title("Job Shop Transport Optimizer")
        self.geometry("1200x700")
        
        # Motyw i kolory
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Stwórz główny layout
        self.create_widgets()
    
    def create_widgets(self):
        """Tworzy wszystkie komponenty GUI"""
        
        # --- GÓRNY PANEL: Tytuł ---
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Job Shop Scheduling with Transport Times Optimizer",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")
        
        # --- LEWY PANEL: Parametry ---
        left_panel = ctk.CTkFrame(self)
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Sekcja: Wczytywanie instancji
        instance_label = ctk.CTkLabel(
            left_panel,
            text="Instance",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        instance_label.pack(anchor="w", pady=(0, 10))
        
        self.instance_file = ctk.CTkEntry(left_panel, placeholder_text="No file selected")
        self.instance_file.pack(fill="x", pady=5)
        
        load_btn = ctk.CTkButton(
            left_panel,
            text="Load Instance",
            command=self.load_instance
        )
        load_btn.pack(fill="x", pady=5)
        
        # Separator
        separator = ctk.CTkFrame(left_panel, height=2, fg_color="gray30")
        separator.pack(fill="x", pady=15)
        
        # Sekcja: Parametry algorytmu genetycznego
        ga_label = ctk.CTkLabel(
            left_panel,
            text="Genetic Algorithm Parameters",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ga_label.pack(anchor="w", pady=(10, 10))
        
        # Population size
        ctk.CTkLabel(left_panel, text="Population Size:").pack(anchor="w", pady=(5, 0))
        self.population_size = ctk.CTkEntry(left_panel)
        self.population_size.insert(0, "50")
        self.population_size.pack(fill="x", pady=(0, 10))
        
        # Generations
        ctk.CTkLabel(left_panel, text="Generations:").pack(anchor="w", pady=(5, 0))
        self.generations = ctk.CTkEntry(left_panel)
        self.generations.insert(0, "100")
        self.generations.pack(fill="x", pady=(0, 10))
        
        # Mutation probability
        ctk.CTkLabel(left_panel, text="Mutation Probability:").pack(anchor="w", pady=(5, 0))
        self.mutation_prob = ctk.CTkEntry(left_panel)
        self.mutation_prob.insert(0, "0.2")
        self.mutation_prob.pack(fill="x", pady=(0, 10))
        
        # Separator
        separator2 = ctk.CTkFrame(left_panel, height=2, fg_color="gray30")
        separator2.pack(fill="x", pady=15)
        
        # Sekcja: Wybór algorytmu
        algo_label = ctk.CTkLabel(
            left_panel,
            text="Algorithm Selection",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        algo_label.pack(anchor="w", pady=(10, 10))
        
        self.algo_var = tk.StringVar(value="genetic")
        
        genetic_radio = ctk.CTkRadioButton(
            left_panel,
            text="Genetic Algorithm",
            variable=self.algo_var,
            value="genetic"
        )
        genetic_radio.pack(anchor="w", pady=5)
        
        exact_radio = ctk.CTkRadioButton(
            left_panel,
            text="Exact Algorithm",
            variable=self.algo_var,
            value="exact"
        )
        exact_radio.pack(anchor="w", pady=5)
        
        greedy_radio = ctk.CTkRadioButton(
            left_panel,
            text="Greedy Heuristic",
            variable=self.algo_var,
            value="greedy"
        )
        greedy_radio.pack(anchor="w", pady=5)
        
        # Separator
        separator3 = ctk.CTkFrame(left_panel, height=2, fg_color="gray30")
        separator3.pack(fill="x", pady=15)
        
        # Przyciski akcji
        run_btn = ctk.CTkButton(
            left_panel,
            text="▶ Run Optimization",
            command=self.run_optimization,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        run_btn.pack(fill="x", pady=10)
        
        # --- PRAWY PANEL: Wyniki i wizualizacja ---
        right_panel = ctk.CTkFrame(self)
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        results_label = ctk.CTkLabel(
            right_panel,
            text="Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_label.pack(anchor="w", pady=(0, 10))
        
        # Logi/wyniki w textbox
        self.results_text = ctk.CTkTextbox(right_panel, height=300)
        self.results_text.pack(fill="both", expand=True, pady=10)
        
        # Status bar
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color="gray"
        )
        self.status_label.pack(anchor="w")
    
    def load_instance(self):
        """Wczytuj plik instancji"""
        file_path = filedialog.askopenfilename(
            initialdir="../data/instances",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.instance_file.delete(0, tk.END)
            self.instance_file.insert(0, file_path)
            self.update_status(f"Loaded: {file_path.split('/')[-1]}")
    
    def run_optimization(self):
        """Uruchom wybrany algorytm"""
        instance = self.instance_file.get()
        if not instance or instance == "No file selected":
            messagebox.showerror("Error", "Please load an instance first!")
            return
        
        algo = self.algo_var.get()
        self.update_status(f"Running {algo} algorithm...")
        self.results_text.insert("end", f"\n{'='*50}\n")
        self.results_text.insert("end", f"Algorithm: {algo.upper()}\n")
        self.results_text.insert("end", f"Instance: {instance}\n")
        
        if algo == "genetic":
            pop_size = self.population_size.get()
            gens = self.generations.get()
            mut_prob = self.mutation_prob.get()
            self.results_text.insert("end", f"Population: {pop_size}, Generations: {gens}, Mutation: {mut_prob}\n")
        
        self.results_text.insert("end", "Status: Optimization completed!\n")
        self.update_status("Optimization completed!")
    
    def update_status(self, message):
        """Aktualizuj status bar"""
        self.status_label.configure(text=message)


def main():
    app = JobShopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
