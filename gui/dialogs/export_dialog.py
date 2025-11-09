import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path


class ExportDialog(ctk.CTkToplevel):
    """Modal dialog dla wyboru eksportu"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Export Schedule")
        self.geometry("450x420")
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
        
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Content frame
        content = ctk.CTkFrame(main_frame, fg_color="#161b22")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Section: Format Selection
        format_label = ctk.CTkLabel(
            content,
            text="Export Formats",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        format_label.pack(anchor="w", pady=(0, 12))
        
        # Checkboxy w frame'u
        check_frame = ctk.CTkFrame(content, fg_color="#0d1117", corner_radius=8)
        check_frame.pack(fill="x", pady=(0, 20))
        
        self.csv_check = ctk.CTkCheckBox(
            check_frame,
            text="CSV (Table with operation details)",
            variable=self.csv_var,
            font=("Segoe UI", 11),
            fg_color="#0078ff",
            hover_color="#0066cc"
        )
        self.csv_check.pack(anchor="w", padx=12, pady=8)
        
        self.json_check = ctk.CTkCheckBox(
            check_frame,
            text="JSON (Structured data format)",
            variable=self.json_var,
            font=("Segoe UI", 11),
            fg_color="#0078ff",
            hover_color="#0066cc"
        )
        self.json_check.pack(anchor="w", padx=12, pady=8)
        
        self.png_check = ctk.CTkCheckBox(
            check_frame,
            text="PNG (Gantt chart visualization)",
            variable=self.png_var,
            font=("Segoe UI", 11),
            fg_color="#0078ff",
            hover_color="#0066cc"
        )
        self.png_check.pack(anchor="w", padx=12, pady=8)
        
        # Section: Save Location
        path_label = ctk.CTkLabel(
            content,
            text="Save Location",
            font=("Segoe UI", 12, "bold"),
            text_color="#ffffff"
        )
        path_label.pack(anchor="w", pady=(20, 12))
        
        # Path frame
        path_frame = ctk.CTkFrame(content, fg_color="#0d1117", corner_radius=8)
        path_frame.pack(fill="x", pady=(0, 20))
        
        self.path_label = ctk.CTkLabel(
            path_frame,
            text="Click Browse to select folder",
            text_color="#8b949e",
            font=("Segoe UI", 10)
        )
        self.path_label.pack(side="left", padx=12, pady=12)
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            command=self._browse_folder,
            fg_color="#0078ff",
            hover_color="#0066cc",
            width=100,
            font=("Segoe UI", 11, "bold")
        )
        browse_btn.pack(side="right", padx=12, pady=8)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="#161b22")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            fg_color="#da3633",
            hover_color="#f85149",
            font=("Segoe UI", 11, "bold"),
            height=35
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save,
            fg_color="#238636",
            hover_color="#2ea043",
            font=("Segoe UI", 11, "bold"),
            height=35
        )
        save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def _browse_folder(self):
        """Wybierz folder"""
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.save_path = Path(folder)
            self.path_label.configure(
                text=str(self.save_path),
                text_color="#ffffff"
            )
    
    def _on_save(self):
        """Zapisz"""
        if not self.save_path:
            self.path_label.configure(
                text="Please choose a folder first!",
                text_color="#ff0000"
            )
            return
        
        if not (self.csv_var.get() or self.json_var.get() or self.png_var.get()):
            self.path_label.configure(
                text="Select at least one export format!",
                text_color="#ff0000"
            )
            return
        
        self.result = {
            'path': self.save_path,
            'csv': self.csv_var.get(),
            'json': self.json_var.get(),
            'png': self.png_var.get()
        }
        self.destroy()
    
    def _on_cancel(self):
        """Anuluj"""
        self.result = None
        self.destroy()
