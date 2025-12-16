import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patheffects as path_effects

# --- CONFIGURATION (GitHub Dark Theme Palette) ---
BG_COLOR = "#161b22"       # Tło ramki
PLOT_AREA_BG = "#0d1117"   # Tło samego obszaru wykresu (ciemniejsze)
AXIS_COLOR = "#8b949e"     # Szary tekst osi
TEXT_COLOR = "#e6edf3"     # Główny tekst
GRID_COLOR = "#30363d"     # Kolor siatki
STRIPE_COLOR = "#1c2128"   # Kolor pasków (zebra striping)

class GanttFrame(ctk.CTkFrame):
    """
    Ramka z wykresem Gantta - Wersja High-Readability.
    Zebra striping, inteligentny kontrast tekstu, wyraźna siatka.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Tytuł
        title_label = ctk.CTkLabel(
            self,
            text="Gantt Chart Visualization",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w", pady=(0, 5), padx=5)
        
        # Kontener na wykres
        self.canvas_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Stan
        self.canvas = None
        self.fig = None
        self.ax = None
        self._color_cache = {}
        
        # Start
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Wyświetl elegancki ekran powitalny"""
        self._clear_canvas()
        
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=BG_COLOR)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(BG_COLOR)
        self.ax.axis('off')
        
        self.ax.text(
            0.5, 0.60,
            "Welcome to Job Shop Optimizer",
            ha='center', va='center',
            fontsize=22, color=TEXT_COLOR, weight='bold',
            fontfamily='sans-serif',
            transform=self.ax.transAxes
        )
        
        self.ax.text(
            0.5, 0.40,
            "The Gantt Chart will appear here",
            ha='center', va='center',
            fontsize=12, color="#58a6ff",
            fontfamily='sans-serif',
            transform=self.ax.transAxes
        )
        
        self._embed_canvas()
    
    def draw_gantt(self, instance, solution):
        """Rysuje maksymalnie czytelny wykres Gantta"""
        self._clear_canvas()
        
        # Setup figury
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=BG_COLOR)
        self.fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.15)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(PLOT_AREA_BG) # Ciemniejsze tło obszaru danych
        
        # Logika
        self._update_color_cache(instance)
        batch_data = self._prepare_data(instance, solution)
        makespan = self._calculate_makespan(batch_data)
        
        # Renderowanie warstwami (Kolejność ma znaczenie!)
        self._render_zebra_stripes(instance)        # 1. Paski tła (Zebra)
        self._render_grid(instance, makespan)       # 2. Siatka pionowa
        self._render_bars(batch_data)               # 3. Słupki zadań
        self._render_labels(batch_data, len(batch_data)) # 4. Teksty na słupkach
        self._setup_axes(instance, makespan)        # 5. Osie i opisy
        
        self._embed_canvas()
    
    def _embed_canvas(self):
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

    def _update_color_cache(self, instance):
        if len(self._color_cache) != len(instance.jobs):
            self._color_cache.clear()
            # 'Set3' lub 'Paired' dają lepszy kontrast dla oczu niż 'turbo'
            # Używamy tab20 dla dużej liczby zadań, Set3 dla mniejszej
            cmap_name = 'tab20' if len(instance.jobs) > 12 else 'Set3'
            cmap = plt.cm.get_cmap(cmap_name)
            
            for job_id in range(len(instance.jobs)):
                # Normalizacja, aby kolory były unikalne
                self._color_cache[job_id] = cmap(job_id % 20)

    def _prepare_data(self, instance, solution):
        data = []
        for i, (job_id, op_id) in enumerate(solution.operation_sequence):
            start = solution.start_times[i]
            op = instance.jobs[job_id].operations[op_id]
            data.append({
                'machine': op.machine_id,
                'start': start,
                'duration': op.processing_time,
                'job_id': job_id,
                'color': self._color_cache[job_id]
            })
        return data

    def _calculate_makespan(self, data):
        return max([b['start'] + b['duration'] for b in data]) if data else 0

    def _render_zebra_stripes(self, instance):
        """Rysuje naprzemienne paski w tle (jak w Excelu) dla czytelności wierszy"""
        for i in range(instance.num_machines):
            if i % 2 == 0:
                # Co drugi wiersz ma nieco jaśniejsze tło
                self.ax.axhspan(i - 0.5, i + 0.5, facecolor=STRIPE_COLOR, alpha=1.0, zorder=0)

    def _render_grid(self, instance, makespan):
        """Rysuje tylko pionową siatkę czasu"""
        self.ax.grid(True, axis='x', color=GRID_COLOR, alpha=0.5, linestyle='--', linewidth=0.8, zorder=1)
        self.ax.set_axisbelow(True)

    def _render_bars(self, data):
        """Słupki z delikatnym obrysem"""
        machines = [d['machine'] for d in data]
        starts = [d['start'] for d in data]
        durations = [d['duration'] for d in data]
        colors = [d['color'] for d in data]
        
        self.ax.barh(
            machines, durations, left=starts, height=0.7, # Wysokość 0.7 daje ładny odstęp
            color=colors, 
            edgecolor="#ffffff", # Biały obrys oddziela zadania od siebie
            linewidth=0.5,
            align='center',
            alpha=0.9,
            zorder=3
        )

    def _render_labels(self, data, count):
        """Etykiety z inteligentnym kolorem (czarny/biały)"""
        if count > 100: fontsize, min_w = 6, 3
        elif count > 50: fontsize, min_w = 8, 2
        else: fontsize, min_w = 9, 1
            
        for d in data:
            if d['duration'] >= min_w:
                center = d['start'] + d['duration'] / 2
                
                # Oblicz kontrast: jeśli tło ciemne -> biały tekst, jeśli jasne -> czarny
                text_color = self._get_contrast_text_color(d['color'])
                
                self.ax.text(
                    center, d['machine'], 
                    f"J{d['job_id']}", 
                    ha='center', va='center',
                    fontsize=fontsize, 
                    color=text_color, 
                    fontweight='bold',
                    zorder=4
                )

    def _get_contrast_text_color(self, bg_color):
        """Oblicza czy tekst powinien być czarny czy biały na podstawie tła"""
        r, g, b, _ = mcolors.to_rgba(bg_color)
        # Wzór na luminancję
        luminance = 0.299*r + 0.587*g + 0.114*b
        return 'black' if luminance > 0.5 else 'white'

    def _setup_axes(self, instance, makespan):
        """Konfiguracja osi"""
        # Oś X
        self.ax.set_xlabel('Time [units]', color=AXIS_COLOR, fontsize=10, labelpad=8)
        self.ax.set_xlim(0, makespan * 1.02) # Start od 0
        
        # Oś Y
        self.ax.set_ylabel('Machines', color=AXIS_COLOR, fontsize=10, labelpad=8)
        self.ax.set_yticks(range(instance.num_machines))
        self.ax.set_yticklabels([f"M{i}" for i in range(instance.num_machines)], color=TEXT_COLOR, fontsize=9, fontweight='bold')
        self.ax.set_ylim(-0.6, instance.num_machines - 0.4)
        
        # Stylizacja ticków
        self.ax.tick_params(axis='x', colors=AXIS_COLOR, labelsize=9)
        self.ax.tick_params(axis='y', colors=BG_COLOR, length=0) # Ukryj kreski Y
        
        # Usunięcie ramki (Spines)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
            
        # Linia zerowa
        self.ax.axvline(x=0, color=GRID_COLOR, linewidth=1)

    def clear(self):
        """Reset"""
        self._clear_canvas()
        self._color_cache.clear()
        self._show_placeholder()