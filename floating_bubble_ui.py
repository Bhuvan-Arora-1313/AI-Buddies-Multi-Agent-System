import tkinter as tk
from tkinter import Toplevel, Label, Text, Entry, Scrollbar, END
import threading

from buddy_magic import run_buddy_system
from shared_queue import swe_messages, pa_messages, swe_inputs, pa_inputs


class BuddyPopup:
    def __init__(self, root, title, messages, inputs, x_offset):
        self.messages = messages
        self.inputs = inputs

        self.bubble = tk.Toplevel(root)
        self.bubble.overrideredirect(True)
        self.bubble.wm_attributes("-topmost", 1)
        self.bubble.geometry(f"60x60+{x_offset}+600")
        self.bubble.configure(bg="#6c5ce7")
        self.bubble.bind("<Button-1>", self.toggle_popup)

        self.canvas = tk.Canvas(self.bubble, width=60, height=60, bg="#6c5ce7", highlightthickness=0)
        self.canvas.create_oval(5, 5, 55, 55, fill="#a29bfe")
        self.canvas.pack()

        self.popup = None
        self.title = title

        self.bubble.after(1000, self.check_for_updates)

    def toggle_popup(self, event=None):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        else:
            self.show_popup()

    def show_popup(self):
        self.popup = Toplevel()
        self.popup.wm_attributes("-topmost", 1)
        self.popup.geometry("400x300+100+400")
        self.popup.configure(bg="white")

        self.popup.title(self.title)

        Label(self.popup, text=self.title, font=("Arial", 14, "bold"), bg="white").pack(pady=5)

        self.text_widget = Text(self.popup, height=10, wrap="word", bg="white", fg="black", font=("Segoe UI", 10))
        self.text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.text_widget.config(state=tk.DISABLED)

        scrollbar = Scrollbar(self.popup, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry = Entry(self.popup, font=("Segoe UI", 10))
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.send_prompt)

        self.refresh_popup()

    def refresh_popup(self):
        if self.popup and self.popup.winfo_exists():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, END)
            for msg in self.messages:
                self.text_widget.insert(END, msg + "\n\n")
            self.text_widget.config(state=tk.DISABLED)
            self.text_widget.see(END)

    def send_prompt(self, event=None):
        prompt = self.entry.get().strip()
        if prompt:
            self.inputs.append(prompt)
            self.entry.delete(0, END)

    def check_for_updates(self):
        self.refresh_popup()
        self.bubble.after(2000, self.check_for_updates)


if __name__ == "__main__":
    threading.Thread(target=run_buddy_system, daemon=True).start()

    root = tk.Tk()
    root.title("Buddy System")  # ✅ Give root a title
    root.geometry("1x1+0+0")  # ✅ Hide it visually but not technically
    # root.withdraw()

    swe_ui = BuddyPopup(root, "👨‍💻 SWE Buddy", swe_messages, swe_inputs, x_offset=100)
    pa_ui = BuddyPopup(root, "🤖 PA Buddy", pa_messages, pa_inputs, x_offset=20)

    root.mainloop()