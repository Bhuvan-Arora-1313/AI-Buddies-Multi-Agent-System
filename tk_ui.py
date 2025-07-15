import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time

# Create a shared queue for buddy messages
buddy_response_queue = queue.Queue()

# Simulated function (replace this with real connection to your buddy system)
def simulate_buddy_updates():
    while True:
        time.sleep(5)
        buddy_response_queue.put({
            "activity": "coding",
            "buddy": "SWE Buddy",
            "response": "Catch FileNotFoundError directly, don’t use broad exceptions."
        })
        time.sleep(10)
        buddy_response_queue.put({
            "activity": "researching",
            "buddy": "PA Buddy",
            "response": "• Gupta Empire was India’s Classical Age\n• Focus is on Indus Valley and Vedic periods"
        })

# Main Tkinter UI
def run_ui():
    window = tk.Tk()
    window.title("🧠 AI Buddies Dashboard")
    window.geometry("700x450")

    # Labels
    activity_label = tk.Label(window, text="Current Activity:", font=("Arial", 14))
    activity_label.pack(pady=10)

    buddy_label = tk.Label(window, text="Triggered Buddy:", font=("Arial", 12))
    buddy_label.pack()

    # Textbox
    response_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=15, font=("Consolas", 10))
    response_box.pack(pady=15)

    # Polling function to update UI
    def poll_queue():
        try:
            while True:
                update = buddy_response_queue.get_nowait()
                activity_label.config(text=f"Current Activity: {update['activity']}")
                buddy_label.config(text=f"Triggered Buddy: {update['buddy']}")
                response_box.insert(tk.END, f"\n[{update['buddy']}]:\n{update['response']}\n\n")
                response_box.yview(tk.END)
        except queue.Empty:
            pass
        window.after(1000, poll_queue)

    window.after(1000, poll_queue)
    window.mainloop()

# Start background thread for simulated updates
threading.Thread(target=simulate_buddy_updates, daemon=True).start()

# Start UI
run_ui()