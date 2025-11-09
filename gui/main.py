import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import sys
import os
from pathlib import Path
import time

# DLL path setup
if sys.platform == "win32":
    msys_bin = r"C:\msys64\ucrt64\bin"
    if os.path.exists(msys_bin):
        os.add_dll_directory(msys_bin)

sys.path.insert(0, str(Path(__file__).parent.parent / "build"))

try:
    import jobshop_bindings as jb
    BINDINGS_AVAILABLE = True
except ImportError as e:
    BINDINGS_AVAILABLE = False
    IMPORT_ERROR = str(e)

sys.path.insert(0, str(Path(__file__).parent))

from widgets import HeaderFrame, SidebarFrame, ConsoleFrame, GanttFrame, ButtonsFrame
from config import WINDOW_WIDTH, WINDOW_HEIGHT


class JobShopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Job Shop Transport Optimizer")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.instance = None
        self.best_solution = None
        self.is_running = False
        
        if not BINDINGS_AVAILABLE:
            messagebox.showerror(
                "Error",
                f"Failed to import jobshop_bindings!\n\n{IMPORT_ERROR}\n\n"
                "Make sure you:\n"
                "1. Ran: cmake --build --preset=default\n"
                "2. Have build/ folder with jobshop_bindings.pyd"
            )
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create UI layout"""
        self.configure(fg_color="#0d1117")
        
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=0)
        header_frame.pack(side="top", fill="x", padx=0, pady=0)
        
        self.header = HeaderFrame(header_frame, bindings_available=BINDINGS_AVAILABLE)
        self.header.pack(fill="x", padx=15, pady=10)
        
        # --- MAIN CONTAINER ---
        main_container = ctk.CTkFrame(self, fg_color="#0d1117")
        main_container.pack(side="top", fill="both", expand=True, padx=15, pady=15)
        
        # --- LEFT PANEL: Two cards ---
        left_panel = ctk.CTkFrame(main_container, fg_color="#0d1117")
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 15))
        left_panel.configure(width=350)
        
                # Top card: Parameters
        params_card = ctk.CTkFrame(
            left_panel,
            fg_color="#161b22"
        )
        params_card.pack(fill="both", expand=True, padx=0, pady=(0, 15))
        
        self.sidebar = SidebarFrame(
            params_card,
            on_instance_load=self.load_instance
        )
        self.sidebar.pack(fill="both", expand=True, padx=15, pady=15)
        self.sidebar.configure(fg_color="#161b22")
        
        # Bottom card: Buttons
        buttons_card = ctk.CTkFrame(
            left_panel,
            fg_color="#161b22"
        )
        buttons_card.pack(fill="x", padx=0, pady=0)
        
        self.buttons = ButtonsFrame(
            buttons_card,
            on_optimize=self.run_optimization,
            on_clear=self.clear_results
        )
        self.buttons.pack(fill="both", expand=True, padx=15, pady=15)
        self.buttons.configure(fg_color="#161b22")
        
        # --- RIGHT PANEL: Content ---
        right_container = ctk.CTkFrame(main_container, fg_color="#0d1117")
        right_container.pack(side="right", fill="both", expand=True)
        
        # Gantt Card
        gantt_card = ctk.CTkFrame(
            right_container,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        gantt_card.pack(fill="both", expand=True, pady=(0, 15))
        
        self.gantt = GanttFrame(gantt_card)
        self.gantt.pack(fill="both", expand=True, padx=15, pady=15)
        self.gantt.configure(fg_color="#161b22")
        
        # Logs Card
        logs_card = ctk.CTkFrame(
            right_container,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        logs_card.pack(fill="both", expand=False, pady=0)
        logs_card.configure(height=180)
        
        self.console = ConsoleFrame(logs_card)
        self.console.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.console.configure(fg_color="#161b22")
    
    def load_instance(self):
        """Load instance from file"""
        file_path = filedialog.askopenfilename(
            initialdir="data/instances",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.instance = jb.load_instance_from_file(file_path)
                
                jobs = len(self.instance.jobs)
                machines = self.instance.num_machines
                
                self.console.insert_log(f"\n{'='*60}\n")
                self.console.insert_log(f"Instance loaded: {Path(file_path).name}\n")
                self.console.insert_log(f"Jobs: {jobs}, Machines: {machines}\n")
                self.console.insert_log(f"{'='*60}\n")
                
                # Wyświetl w headerze
                self.header.set_instance_info(Path(file_path).name, jobs, machines)
                self.header.update_status("Ready", "#8b949e")
                
                # Włącz przycisk
                self.buttons.enable_optimize()
                
                return (file_path, jobs, machines)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load instance:\n{str(e)}")
                self.header.update_status(f"Error: {str(e)}", "#ff0000")
                return None
        
        return None
    
    def run_optimization(self):
        """Run optimization in separate thread"""
        if not self.instance:
            messagebox.showerror("Error", "Please load an instance first!")
            return
        
        params = self.sidebar.get_parameters()
        if not params:
            messagebox.showerror("Error", "Invalid parameter values!")
            return
        
        self.is_running = True
        self.buttons.disable_optimize()
        
        thread = threading.Thread(
            target=self._run_optimization_thread,
            args=(params,)
        )
        thread.daemon = True
        thread.start()
    
    def _run_optimization_thread(self, params):
        """Execute optimization in thread"""
        try:
            self.header.update_status("Running optimization...", "#ffaa00")
            
            # Shortened logs
            self.console.insert_log("GA started...\n")
            
            start_time = time.time()
            self.best_solution = jb.run_genetic(
                self.instance,
                params['population_size'],
                params['generations'],
                params['tournament_size'],
                params['mutation_prob'],
                params['seed']
            )
            elapsed_time = time.time() - start_time
            
            makespan = jb.calculate_makespan(self.instance, self.best_solution)
            
            # Minimal logs
            self.console.insert_log(f"Completed in {elapsed_time:.2f}s\n")
            self.console.insert_log(f"Makespan: {makespan}\n")
            
            self.gantt.draw_gantt(self.instance, self.best_solution)
            
            self.header.update_status(
                f"Completed in {elapsed_time:.2f}s - Makespan: {makespan}",
                "#00ff00"
            )
            
        except Exception as e:
            self.console.insert_log(f"Error: {str(e)}\n")
            self.header.update_status(f"Error: {str(e)}", "#ff0000")
        finally:
            self.is_running = False
            self.buttons.enable_optimize()

    def clear_results(self):
        """Clear all results"""
        self.console.clear()
        self.gantt.clear()
        self.best_solution = None
        # self.header.reset_instance_info()
        self.header.update_status("Ready", "#8b949e")
    
    def update_status(self, message):
        """Update status in header"""
        self.header.update_status(message)


def main():
    app = JobShopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
