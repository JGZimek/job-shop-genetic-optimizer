import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class GanttFrame(ctk.CTkFrame):
    """Ramka z wykresem Gantta - profesjonalny"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Tytuł
        title_label = ctk.CTkLabel(
            self,
            text="Gantt Chart",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Canvas frame
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Zmienne
        self.canvas = None
        self.fig = None
        self.ax = None
        self._color_cache = {}
        
        # Wyświetl placeholder na starcie
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Wyświetl placeholder zanim będzie pierwszy wykres"""
        self._clear_canvas()
        
        # Utwórz figurę z placeholder
        self.fig = Figure(figsize=(13, 6), dpi=100, facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111)
        
        # Tekst
        self.ax.text(
            0.5, 0.7,
            "Welcome to Job Shop Optimizer",
            ha='center', va='center',
            fontsize=24, color='#ffffff', weight='bold',
            transform=self.ax.transAxes
        )
        
        self.ax.text(
            0.5, 0.55,
            "1. Load an instance from 'Browse Files'",
            ha='center', va='center',
            fontsize=12, color='#8b949e',
            transform=self.ax.transAxes
        )
        
        self.ax.text(
            0.5, 0.45,
            "2. Adjust GA parameters if needed",
            ha='center', va='center',
            fontsize=12, color='#8b949e',
            transform=self.ax.transAxes
        )
        
        self.ax.text(
            0.5, 0.35,
            "3. Click 'Run Optimization'",
            ha='center', va='center',
            fontsize=12, color='#8b949e',
            transform=self.ax.transAxes
        )
        
        self.ax.text(
            0.5, 0.20,
            "The Gantt Chart will appear here",
            ha='center', va='center',
            fontsize=11, color='#0078ff', weight='bold',
            transform=self.ax.transAxes
        )
        
        # Usuń osie
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.ax.set_facecolor('#2a2a2a')
        
        # Osadź canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def draw_gantt(self, instance, solution):
        """Narysuj Gantt Chart"""
        self._clear_canvas()
        
        # Tworzenie figury
        self.fig = Figure(figsize=(13, 6), dpi=100, facecolor='#1a1a1a')
        self.fig.subplots_adjust(left=0.1, right=0.96, top=0.93, bottom=0.12)
        self.ax = self.fig.add_subplot(111)
        
        # Cache kolorów
        self._update_color_cache(instance)
        
        # Przygotowanie danych
        batch_data = self._prepare_data(instance, solution)
        makespan = self._calculate_makespan(batch_data)
        
        # Renderowanie
        self._render_bars(batch_data)
        self._render_labels(batch_data, len(batch_data))
        self._setup_axes(instance, makespan)
        
        # Osadzenie canvasu
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _update_color_cache(self, instance):
        """Zaaktualizuj cache kolorów"""
        if len(self._color_cache) != len(instance.jobs):
            self._color_cache.clear()
            cmap = plt.cm.get_cmap('tab20' if len(instance.jobs) <= 20 else 'hsv')
            for job_id in range(len(instance.jobs)):
                self._color_cache[job_id] = cmap(job_id / max(len(instance.jobs), 1))
    
    def _prepare_data(self, instance, solution):
        """Przygotuj dane do renderowania"""
        batch_data = []
        
        for i, (job_id, op_id) in enumerate(solution.operation_sequence):
            start_time = solution.start_times[i]
            operation = instance.jobs[job_id].operations[op_id]
            duration = operation.processing_time
            
            batch_data.append({
                'machine': operation.machine_id,
                'start': start_time,
                'duration': duration,
                'job_id': job_id,
                'op_id': op_id,
                'color': self._color_cache[job_id]
            })
        
        return batch_data
    
    def _calculate_makespan(self, batch_data):
        """Oblicz makespan"""
        return max([b['start'] + b['duration'] for b in batch_data]) if batch_data else 0
    
    def _render_bars(self, batch_data):
        """Renderuj słupki"""
        machines = [b['machine'] for b in batch_data]
        starts = [b['start'] for b in batch_data]
        durations = [b['duration'] for b in batch_data]
        colors = [b['color'] for b in batch_data]
        
        self.ax.barh(
            machines, durations, left=starts, height=0.65,
            color=colors, edgecolor='#ffffff', linewidth=1.2,
            alpha=0.95, capstyle='butt'
        )
    
    def _render_labels(self, batch_data, num_total):
        """Renderuj etykiety na słupkach"""
        # Dostosuj fontsize i warunki w zależności od liczby operacji
        if num_total <= 50:
            fontsize = 8
            min_duration = 0.5
        elif num_total <= 100:
            fontsize = 6
            min_duration = 0.5
        else:
            fontsize = 5
            min_duration = 1.0
        
        for b in batch_data:
            if b['duration'] >= min_duration:
                self.ax.text(
                    b['start'] + b['duration'] / 2, b['machine'],
                    f"J{b['job_id']}", 
                    ha='center', va='center',
                    fontsize=fontsize, color='#000000', weight='bold',
                    bbox=dict(
                        boxstyle='round,pad=0.3', 
                        facecolor='#ffff00',
                        alpha=0.8, 
                        edgecolor='#ffffff', 
                        linewidth=0.5
                    )
                )
    
    def _setup_axes(self, instance, makespan):
        """Skonfiguruj osie"""
        self.ax.set_xlabel('Time', color='#ffffff', fontsize=12, weight='bold', labelpad=10)
        self.ax.set_ylabel('Machine', color='#ffffff', fontsize=12, weight='bold', labelpad=10)
        
        self.ax.set_yticks(range(instance.num_machines))
        self.ax.set_yticklabels(
            [f"M{i}" for i in range(instance.num_machines)],
            fontsize=10, color='#ffffff', weight='bold'
        )
        
        self.ax.set_xlim(-2, makespan * 1.08)
        self.ax.set_ylim(-0.7, instance.num_machines - 0.3)
        
        self.ax.grid(True, axis='x', alpha=0.25, color='#ffffff', linestyle='--', linewidth=0.6)
        self.ax.grid(True, axis='y', alpha=0.15, color='#ffffff', linestyle='-', linewidth=0.4)
        
        self.ax.tick_params(colors='#ffffff', labelsize=9, width=1.5, length=5)
        
        self.ax.set_facecolor('#2a2a2a')
        
        for spine in self.ax.spines.values():
            spine.set_color('#ffffff')
            spine.set_linewidth(1.5)
    
    def _clear_canvas(self):
        """Wyczyść canvas"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None
    
    def clear(self):
        """Wyczyść całą ramkę"""
        self._clear_canvas()
        self._color_cache.clear()
        self._show_placeholder()
