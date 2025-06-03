# themes.py
import os
import json

THEMES = {
    "light": {
        "bg": '#ADD8E6',
        "button_bg": '#FFFFE0',
        "entry_bg": '#FFFFFF',
        "fg": 'black',
        "border_color": 'black',
        "table_bg": '#ADD8E6',
        "table_fg": 'black',
        "table_border": 'black',
        "card_bg": "#ffffff",
        "scroll_bg": "#e0e0e0",
        "scroll_trough": "#cccccc",
        "scroll_border": "#888888",
        "scroll_arrow": "#444444",
        "table_head_bg": "#b0c4de",
        "table_head_fg": "black",
        "notif_container_bg": "#ADD8E6",  # or any other color you want
        "danger": "#F01027",          # Red
        "warning": "#FCF802",         # Yellow
        "safe": "#A1A79D",            # Green
        "notif_container_bg": "#ADD8E6",
        "info": "#6FBCCA"  # Orange for missing purchase


    },
    "dark": {
        "bg": '#121212',
        "button_bg": '#3a3f47',
        "entry_bg": '#2a2f37',
        "fg": 'white',
        "border_color": 'white',
        "table_bg": '#121212',
        "table_fg": 'white',
        "table_border": 'white',
        "card_bg": "#2a2a2a",
        "scroll_bg": "#2a2a2a",
        "scroll_trough": "#3a3a3a",
        "scroll_border": "#555555",
        "scroll_arrow": "#bbbbbb",
        "table_head_bg": "#444444",
        "table_head_fg": "white",
        "danger": "#BF616A",          # Red
        "warning": "#EBCB8B",         # Yellow
        "safe": "#A3BE8C",            # Green
        "notif_container_bg":"#121212",
        "info": "#FF8C00"  # Orange for missing purchase

    }
}

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".trackedge_config.json")

def load_theme():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return config.get('theme', 'light')
    except Exception:
        pass
    return 'light'

def save_theme(theme):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump({'theme': theme}, f)
    except Exception:
        pass
