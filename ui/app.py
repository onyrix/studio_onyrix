import tkinter as tk

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Onyrix AI DAW")

        self.label = tk.Label(self.root, text="AI MIDI DAW Ready")
        self.label.pack()

    def run(self):
        self.root.mainloop()