import os

PAUSE_FILE = "pause.flag"

def is_paused():
    return os.path.exists(PAUSE_FILE)

def set_paused(value: bool):
    if value:
        with open(PAUSE_FILE, "w") as f:
            f.write("1")
    else:
        if os.path.exists(PAUSE_FILE):
            os.remove(PAUSE_FILE)