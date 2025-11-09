import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class GanttFrame(ctk.CTkFrame):
    """Ramka z wykresem Gantta - wyraźna i czytelna"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        title_label = ctk.CTkLabel(
            self,
            text="Gantt Chart",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = None
        self.fig = None
        self.ax = None
        self._color_cache = {}
    
    def draw_gantt(self, instance, solution):
        """Narysuj Gantt - wyraźny i profesjonalny"""
        self._clear_canvas()
        
        # Większy DPI dla lepszej jakości
        self.fig = Figure(figsize=(13, 6), dpi=100, facecolor='#1a1a1a')
        self.fig.subplots_adjust(left=0.1, right=0.96, top=0.93, bottom=0.12)
        self.ax = self.fig.add_subplot(111)
        
        # Lepsze kolory - bardziej nasycone
        if len(self._color_cache) != len(instance.jobs):
            self._color_cache.clear()
            cmap = plt.cm.get_cmap('tab20' if len(instance.jobs) <= 20 else 'hsv')
            for job_id in range(len(instance.jobs)):
                self._color_cache[job_id] = cmap(job_id / max(len(instance.jobs), 1))
        
        # Zbierz dane
        makespan = 0
        batch_data = []
        
        for i, (job_id, op_id) in enumerate(solution.operation_sequence):
            start_time = solution.start_times[i]
            operation = instance.jobs[job_id].operations[op_id]
            duration = operation.processing_time
            machine_id = operation.machine_id
            end_time = start_time + duration
            
            if end_time > makespan:
                makespan = end_time
            
            batch_data.append({
                'machine': machine_id,
                'start': start_time,
                'duration': duration,
                'job_id': job_id,
                'op_id': op_id,
                'color': self._color_cache[job_id]
            })
        
        # Render z lepszą wizualizacją
        machines = [b['machine'] for b in batch_data]
        starts = [b['start'] for b in batch_data]
        durations = [b['duration'] for b in batch_data]
        colors = [b['color'] for b in batch_data]
        
        # Grubsze krawędzie dla lepszej czytelności
        self.ax.barh(machines, durations, left=starts, height=0.65,
                     color=colors, edgecolor='#ffffff', linewidth=1.2, 
                     alpha=0.95, capstyle='butt')
        
        # Labels na każdym barze
        for b in batch_data:
            if b['duration'] > 2:  # Rysuj label tylko dla dłuższych baru
                self.ax.text(
                    b['start'] + b['duration']/2, b['machine'],
                    f"J{b['job_id']}O{b['op_id']}", 
                    ha='center', va='center',
                    fontsize=8, color='#000000', weight='bold',
                    bbox=dict(boxstyle='round,pad=0.35', facecolor='#ffff00', 
                             alpha=0.7, edgecolor='#ffffff', linewidth=0.5)
                )
        
        # Setup osi - bardziej wyraźnie
        self.ax.set_xlabel('Time', color='#ffffff', fontsize=12, weight='bold', labelpad=10)
        self.ax.set_ylabel('Machine', color='#ffffff', fontsize=12, weight='bold', labelpad=10)
        
        self.ax.set_yticks(range(instance.num_machines))
        self.ax.set_yticklabels([f"M{i}" for i in range(instance.num_machines)], 
                                fontsize=10, color='#ffffff', weight='bold')
        
        self.ax.set_xlim(-2, makespan * 1.08)
        self.ax.set_ylim(-0.7, instance.num_machines - 0.3)
        
        # Lepszy grid
        self.ax.grid(True, axis='x', alpha=0.25, color='#ffffff', linestyle='--', linewidth=0.6)
        self.ax.grid(True, axis='y', alpha=0.15, color='#ffffff', linestyle='-', linewidth=0.4)
        
        self.ax.tick_params(colors='#ffffff', labelsize=9, width=1.5, length=5)
        
        # Tło
        self.ax.set_facecolor('#2a2a2a')
        
        # Spines - wyraźniejsze
        for spine in self.ax.spines.values():
            spine.set_color('#ffffff')
            spine.set_linewidth(1.5)
        
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _clear_canvas(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None
    
    def clear(self):
        self._clear_canvas()
        self._color_cache.clear()
