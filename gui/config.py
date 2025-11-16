"""Współdzielone konfiguracje GUI"""

# Kolory
DARK_BG = "#0d1117"        # Główne tło (ciemniejsze)
CARD_BG = "#161b22"        # Tło kafelka
LIGHT_BG = "#2b2b2b"
ACCENT_COLOR = "#0078ff"
TEXT_COLOR = "#ffffff"
TEXT_SECONDARY = "#8b949e"
BORDER_COLOR = "#30363d"

# Rozmiary
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 350
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)

# Parametry domyślne
DEFAULT_PARAMS = {
    "population_size": 30,
    "generations": 100,
    "tournament_size": 3,
    "mutation_prob": 0.2,
    "seed": 0,
}

# Ścieżki
DATA_DIR = "data/instances"

# Card styling (dla kafelków)
CARD_PADX = 15
CARD_PADY = 15
CORNER_RADIUS = 10
BORDER_WIDTH = 1
