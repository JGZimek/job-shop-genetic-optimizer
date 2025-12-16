import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import os

class ExportDialog(ctk.CTkToplevel):
    """
    Kompaktowe okno wyboru eksportu.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Export")
        self.geometry("340x320") # Znacznie mniejszy rozmiar
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Zmienne
        self.csv_var = ctk.BooleanVar(value=True)
        self.json_var = ctk.BooleanVar(value=False)
        self.png_var = ctk.BooleanVar(value=False)
        self.save_path = None
        self.result = None
        
        # Główny kontener (bez marginesów zewnętrznych)
        self.configure(fg_color="#161b22")
        
        # --- 1. WYBÓR FORMATU ---
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            format_frame, 
            text="Formats", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#ffffff"
        ).pack(anchor="w", pady=(0, 5))
        
        # Ciemniejsze tło dla checkboxów
        check_bg = ctk.CTkFrame(format_frame, fg_color="#0d1117", border_color="#30363d", border_width=1)
        check_bg.pack(fill="x")
        
        # Checkboxy gęsto upakowane
        self._make_checkbox(check_bg, "CSV (Data Table)", self.csv_var)
        self._make_checkbox(check_bg, "JSON (Raw Data)", self.json_var)
        self._make_checkbox(check_bg, "PNG (Gantt Chart)", self.png_var)
        
        # --- 2. LOKALIZACJA ---
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            path_frame, 
            text="Destination Folder", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#ffffff"
        ).pack(anchor="w", pady=(0, 5))
        
        # Input group (Entry + Button w jednej linii)
        input_group = ctk.CTkFrame(path_frame, fg_color="transparent")
        input_group.pack(fill="x")
        
        # Pole tekstowe (wygląda lepiej niż label) - ReadOnly
        self.path_entry = ctk.CTkEntry(
            input_group,
            placeholder_text="No folder selected...",
            fg_color="#0d1117",
            border_color="#30363d",
            text_color="#e6edf3",
            height=30,
            font=("Segoe UI", 11)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ctk.CTkButton(
            input_group,
            text="Browse",
            command=self._browse_folder,
            fg_color="#0d1117", # Ciemny przycisk
            border_color="#30363d",
            border_width=1,
            hover_color="#1f2428",
            width=70,
            height=30,
            font=("Segoe UI", 11)
        )
        browse_btn.pack(side="right")
        
        # --- 3. PRZYCISKI AKCJI ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            fg_color="transparent",
            border_color="#30363d",
            border_width=1,
            hover_color="#30363d",
            height=32,
            font=("Segoe UI", 11),
            width=80
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Export",
            command=self._on_save,
            fg_color="#238636", # Zielony GitHub
            hover_color="#2ea043",
            height=32,
            font=("Segoe UI", 11, "bold")
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))

    def _make_checkbox(self, parent, text, variable):
        """Helper do tworzenia małych checkboxów"""
        ctk.CTkCheckBox(
            parent,
            text=text,
            variable=variable,
            font=("Segoe UI", 11),
            fg_color="#0078ff",
            hover_color="#0066cc",
            border_width=2,
            checkbox_width=18,
            checkbox_height=18
        ).pack(anchor="w", padx=10, pady=6)

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.save_path = Path(folder)
            # Aktualizacja pola tekstowego
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, str(self.save_path))
            self.path_entry.configure(state="readonly") # Z powrotem tylko do odczytu

    def _on_save(self):
        # Walidacja ścieżki
        if not self.save_path:
            self.path_entry.configure(border_color="#cf222e") # Czerwona ramka błędu
            return
        
        # Sprawdź zapisywalność
        if not os.access(self.save_path, os.W_OK):
             from tkinter import messagebox
             messagebox.showerror("Error", "Selected folder is not writable!")
             return

        # Walidacja formatów
        if not (self.csv_var.get() or self.json_var.get() or self.png_var.get()):
            # Można tu mignąć ramką checkboxów, ale prościej zablokować akcję
            return

        self.result = {
            'path': self.save_path,
            'csv': self.csv_var.get(),
            'json': self.json_var.get(),
            'png': self.png_var.get()
        }
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()