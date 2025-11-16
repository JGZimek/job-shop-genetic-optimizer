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

# Add build/python_module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "build" / "python_module"))

# Try to import bindings
try:
    import bindings as jb
    BINDINGS_AVAILABLE = True
except ImportError as e:
    BINDINGS_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Add gui directory to path
sys.path.insert(0, str(Path(__file__).parent))

from widgets import HeaderFrame, SidebarFrame, ConsoleFrame, GanttFrame, ButtonsFrame
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from utils.export import ScheduleExporter


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
                f"Failed to import bindings!\n\n{IMPORT_ERROR}\n\n"
                "Make sure you:\n"
                "1. Ran: cmake --build --preset=default\n"
                "2. Have build/python_module/bindings.pyd"
            )
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create UI layout"""
        self.configure(fg_color="#0d1117")
        
        # --- HEADER ---
        header_frame = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=0)
        header_frame.pack(side="top", fill="x", padx=15, pady=(15, 10))
        
        self.header = HeaderFrame(header_frame, bindings_available=BINDINGS_AVAILABLE)
        self.header.pack(fill="x")
        
        # --- MAIN CONTAINER ---
        main_container = ctk.CTkFrame(self, fg_color="#0d1117")
        main_container.pack(side="top", fill="both", expand=True, padx=15, pady=15)
        
        # --- LEFT PANEL ---
        left_panel = ctk.CTkFrame(main_container, fg_color="#0d1117")
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 15))
        left_panel.configure(width=350)
        
        # Parameters card
        params_card = ctk.CTkFrame(left_panel, fg_color="#161b22")
        params_card.pack(fill="both", expand=True, padx=0, pady=(0, 15))
        
        self.sidebar = SidebarFrame(
            params_card,
            on_instance_load=self.load_instance
        )
        self.sidebar.pack(fill="both", expand=True, padx=15, pady=15)
        self.sidebar.configure(fg_color="#161b22")
        
        # Buttons card
        buttons_card = ctk.CTkFrame(left_panel, fg_color="#161b22")
        buttons_card.pack(fill="x", padx=0, pady=0)
        
        self.buttons = ButtonsFrame(
            buttons_card,
            on_optimize=self.run_optimization,
            on_clear=self.clear_results,
            on_export=self.export_schedule
        )
        self.buttons.pack(fill="both", expand=True, padx=15, pady=15)
        self.buttons.configure(fg_color="#161b22")
        
        # --- RIGHT PANEL ---
        right_container = ctk.CTkFrame(main_container, fg_color="#0d1117")
        right_container.pack(side="right", fill="both", expand=True)
        
        right_container.grid_rowconfigure(0, weight=75)
        right_container.grid_rowconfigure(1, weight=25)
        right_container.grid_columnconfigure(0, weight=1)
        
        # Gantt card
        gantt_card = ctk.CTkFrame(
            right_container,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        gantt_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        self.gantt = GanttFrame(gantt_card)
        self.gantt.pack(fill="both", expand=True, padx=15, pady=15)
        self.gantt.configure(fg_color="#161b22")
        
        # Logs card
        logs_card = ctk.CTkFrame(
            right_container,
            fg_color="#161b22",
            corner_radius=10,
            border_width=1,
            border_color="#30363d"
        )
        logs_card.grid(row=1, column=0, sticky="nsew", pady=0)
        
        self.console = ConsoleFrame(logs_card)
        self.console.pack(fill="both", expand=True, padx=15, pady=15)
        self.console.configure(fg_color="#161b22")
    
    def load_instance(self):
        """Load instance from file"""
        file_path = filedialog.askopenfilename(
            initialdir="data/instances",
            filetypes=[
                ("All Supported", "*.txt *.csv"),
                ("Text Files", "*.txt"),
                ("CSV Files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return None
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in {'.txt', '.csv'}:
            messagebox.showwarning(
                "Unsupported Format",
                f"Supported: .txt, .csv\nSelected: {file_ext}"
            )
            return None
        
        try:
            file_name = Path(file_path).name
            self.header.update_status(f"Loading {file_name}...", "#ffaa00")
            self.update_idletasks()
            
            self.instance = jb.load_instance_from_file(file_path)
            
            jobs = len(self.instance.jobs)
            machines = self.instance.num_machines
            
            if jobs == 0 or machines == 0:
                raise ValueError("Invalid instance")
            
            seq_sol = jb.Solution()
            for j in range(jobs):
                for op in range(machines):
                    seq_sol.operation_sequence.append((j, op))
            
            baseline = jb.calculate_makespan(self.instance, seq_sol)
            
            self.console.log_loaded(file_name, jobs, machines, baseline)
            
            self.header.set_instance_info(file_name, jobs, machines)
            self.header.update_status("Ready", "#8b949e")
            self.buttons.enable_optimize()
            
            return (file_path, jobs, machines)
        
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Failed to load:\n{error_msg}")
            self.console.log_error(error_msg)
            self.header.update_status("Error", "#ff0000")
            self.instance = None
            return None
    
    def run_optimization(self):
        """Run optimization in separate thread"""
        if not self.instance:
            messagebox.showerror("Error", "Load instance first!")
            return
        
        params = self.sidebar.get_parameters()
        if not params:
            messagebox.showerror("Error", "Invalid parameters!")
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
            algorithm = params.get("algorithm", "genetic")
            
            self.header.update_status("Running...", "#ffaa00")
            
            if algorithm == "genetic":
                self.console.log_ga_params(params)
            
            self.console.log_running(algorithm.capitalize())
            self.update_idletasks()
            
            start_time = time.time()
            
            if algorithm == "genetic":
                self.best_solution = jb.run_genetic(
                    self.instance,
                    params['population_size'],
                    params['generations'],
                    params['tournament_size'],
                    params['mutation_prob'],
                    params['seed']
                )
            elif algorithm == "greedy":
                self.best_solution = jb.greedy_schedule(self.instance)
            elif algorithm == "exact":
                self.best_solution = jb.solve_exact(self.instance)
            
            elapsed_time = time.time() - start_time
            makespan = jb.calculate_makespan(self.instance, self.best_solution)
            
            self.console.log_completed(makespan, elapsed_time)
            
            self.gantt.draw_gantt(self.instance, self.best_solution)
            self.buttons.enable_export()
            
            self.header.update_status(
                f"Completed: {makespan} ({elapsed_time:.2f}s)",
                "#00ff00"
            )
            
        except Exception as e:
            self.console.log_error(str(e))
            self.header.update_status("Error", "#ff0000")
        finally:
            self.is_running = False
            self.buttons.enable_optimize()

    
    def export_schedule(self):
        """Export schedule"""
        if not self.best_solution or not self.instance:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        from gui.dialogs.export_dialog import ExportDialog
        dialog = ExportDialog(self)
        self.wait_window(dialog)
        
        if not dialog.result:
            return
        
        result = dialog.result
        save_path = result['path']
        
        try:
            exported = []
            
            if result['csv']:
                from datetime import datetime
                filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                path = ScheduleExporter.export_to_csv(
                    self.instance, 
                    self.best_solution, 
                    output_path=save_path / filename
                )
                exported.append(Path(path).name)
                self.console.insert_log(f"Exported: {Path(path).name}\n")
            
            if result['json']:
                from datetime import datetime
                filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                path = ScheduleExporter.export_to_json(
                    self.instance, 
                    self.best_solution, 
                    output_path=save_path / filename
                )
                exported.append(Path(path).name)
                self.console.insert_log(f"Exported: {Path(path).name}\n")
            
            if result['png'] and self.gantt.fig:
                from datetime import datetime
                filename = f"gantt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                path = ScheduleExporter.export_gantt_image(
                    self.gantt.fig, 
                    output_path=save_path / filename
                )
                exported.append(Path(path).name)
                self.console.insert_log(f"Exported: {Path(path).name}\n")
            
            self.header.update_status("Exported!", "#00ff00")
            messagebox.showinfo("Success", f"Exported {len(exported)} files")
            
        except Exception as e:
            self.console.insert_log(f"Export error: {str(e)}\n")
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        self.console.clear()
        self.gantt.clear()
        self.best_solution = None
        self.buttons.disable_export()
        self.header.update_status("Ready", "#8b949e")
    
    def update_status(self, message):
        """Update status in header"""
        self.header.update_status(message)


def main():
    app = JobShopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
