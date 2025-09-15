import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

from utils.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from midi_engine import parse_midi
from visual_engine import VisualEngine
from controller import Controller


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#111111")

        # Top controls
        top = tk.Frame(root, bg="#111111")
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        self.load_btn = tk.Button(top, text="Load MIDI...", command=self.on_load)
        self.load_btn.pack(side=tk.LEFT, padx=4)

        self.play_btn = tk.Button(top, text="Play", command=self.on_play, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=4)

        self.pause_btn = tk.Button(top, text="Pause", command=self.on_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=4)

        self.stop_btn = tk.Button(top, text="Stop", command=self.on_stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        self.file_label = tk.Label(top, text="No file loaded", fg="#DDDDDD", bg="#111111")
        self.file_label.pack(side=tk.LEFT, padx=12)

        # Canvas for visuals
        self.canvas = tk.Canvas(
            root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT - 80,
            bg="#000000", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Visual engine + controller
        self.visual = VisualEngine(self.canvas, WINDOW_WIDTH, WINDOW_HEIGHT - 80)
        self.controller = Controller(self.canvas, self.visual)

        # main loop tick
        self.root.after(1000 // 60, self._on_frame)

        # handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.loaded_path = None

    def on_load(self):
        try:
            path = filedialog.askopenfilename(
                title="Select MIDI file",
                filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
            )
            if not path:
                return
            events, meta = parse_midi(path)
            if not events:
                messagebox.showwarning("MIDI Visualizer", "No note events found in this MIDI.")
                return
            self.controller.load_events(events, meta)
            self.file_label.configure(text=path)
            self.loaded_path = path
            self.play_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error loading MIDI", str(e))

    def on_play(self):
        self.controller.play()

    def on_pause(self):
        self.controller.pause()

    def on_stop(self):
        self.controller.stop()

    def _on_frame(self):
        self.controller.tick(lambda delay: self.root.after(delay, self._on_frame))

    def on_close(self):
        """Clean shutdown of MIDI device + Tkinter."""
        try:
            self.controller.close()
        except Exception as e:
            print("Error closing controller:", e)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
