import tkinter as tk
import random


class ReactionTrainer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reaction Time Trainer")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("500x520")
        self.root.resizable(False, False)

        self.colors = {
            "Red": "#e80000",
            "Blue": "#0055ff",
            "Green": "#00c853",
            "Yellow": "#ffd600",
            "Orange": "#ff6d00",
            "Purple": "#aa00ff",
            "Cyan": "#00e5ff",
            "White": "#ffffff",
            "Black": "#000000",
        }

        self.selected = {name: tk.BooleanVar(value=name in ("Red", "Blue", "Green"))
                         for name in self.colors}
        self.min_dur = tk.IntVar(value=200)
        self.max_dur = tk.IntVar(value=1500)

        self.running = False
        self.flash_after_id = None
        self.flash_window = None

        self._build_home()

    # ── Home Screen ──────────────────────────────────────────────
    def _build_home(self):
        f = tk.Frame(self.root, bg="#1a1a2e")
        f.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(f, text="Reaction Time Trainer", font=("Segoe UI", 20, "bold"),
                 bg="#1a1a2e", fg="#eee").pack(pady=(10, 2))
        tk.Label(f, text="Select colors and timing, then go fullscreen!",
                 font=("Segoe UI", 10), bg="#1a1a2e", fg="#888").pack()

        # ── Colors ──
        box = tk.LabelFrame(f, text="  COLORS  ", font=("Segoe UI", 10, "bold"),
                            bg="#16213e", fg="#aaa", bd=0, padx=14, pady=10)
        box.pack(fill="x", pady=(14, 0))

        row = None
        for i, (name, hex_col) in enumerate(self.colors.items()):
            if i % 3 == 0:
                row = tk.Frame(box, bg="#16213e")
                row.pack(fill="x", pady=2)
            cb = tk.Checkbutton(
                row, text=name, variable=self.selected[name],
                font=("Segoe UI", 11), bg="#16213e", fg="#eee",
                selectcolor="#0f3460", activebackground="#16213e",
                activeforeground="#eee", anchor="w", width=10,
            )
            cb.pack(side="left", padx=4)

        # ── Timing ──
        tbox = tk.LabelFrame(f, text="  TIMING  ", font=("Segoe UI", 10, "bold"),
                             bg="#16213e", fg="#aaa", bd=0, padx=14, pady=10)
        tbox.pack(fill="x", pady=(14, 0))

        self.min_label = tk.Label(tbox, text="Min duration: 0.2s",
                                  font=("Segoe UI", 10), bg="#16213e", fg="#ccc")
        self.min_label.pack(anchor="w")
        min_s = tk.Scale(tbox, from_=50, to=2000, resolution=50, orient="horizontal",
                         variable=self.min_dur, bg="#16213e", fg="#e94560",
                         troughcolor="#0f3460", highlightthickness=0, bd=0,
                         showvalue=False, command=self._on_min_change)
        min_s.pack(fill="x")

        self.max_label = tk.Label(tbox, text="Max duration: 1.5s",
                                  font=("Segoe UI", 10), bg="#16213e", fg="#ccc")
        self.max_label.pack(anchor="w", pady=(6, 0))
        max_s = tk.Scale(tbox, from_=100, to=5000, resolution=50, orient="horizontal",
                         variable=self.max_dur, bg="#16213e", fg="#e94560",
                         troughcolor="#0f3460", highlightthickness=0, bd=0,
                         showvalue=False, command=self._on_max_change)
        max_s.pack(fill="x")

        # ── Start Button ──
        btn = tk.Button(f, text="Start Fullscreen", font=("Segoe UI", 14, "bold"),
                        bg="#e94560", fg="#fff", activebackground="#c73050",
                        activeforeground="#fff", bd=0, padx=30, pady=10,
                        cursor="hand2", command=self._start)
        btn.pack(pady=20)

    def _on_min_change(self, val):
        v = int(val)
        if v > self.max_dur.get():
            self.max_dur.set(v)
            self.max_label.config(text=f"Max duration: {v / 1000:.1f}s")
        self.min_label.config(text=f"Min duration: {v / 1000:.1f}s")

    def _on_max_change(self, val):
        v = int(val)
        if v < self.min_dur.get():
            self.min_dur.set(v)
            self.min_label.config(text=f"Min duration: {v / 1000:.1f}s")
        self.max_label.config(text=f"Max duration: {v / 1000:.1f}s")

    # ── Fullscreen Flash ─────────────────────────────────────────
    def _get_active_colors(self):
        return [hex_c for name, hex_c in self.colors.items()
                if self.selected[name].get()]

    def _start(self):
        active = self._get_active_colors()
        if not active:
            return

        self.running = True
        self.active_colors = active

        # Create fullscreen window
        self.flash_window = tk.Toplevel(self.root)
        self.flash_window.attributes("-fullscreen", True)
        self.flash_window.configure(cursor="none")
        self.flash_window.focus_set()

        # Hint label (fades conceptually – we just remove it after 2s)
        self.hint = tk.Label(self.flash_window, text="Press any key or click to return",
                             font=("Segoe UI", 12), fg="#666", bg="#000")
        self.hint.place(relx=0.5, rely=0.95, anchor="center")
        self.flash_window.after(2000, self._hide_hint)

        # Bind exit events
        self.flash_window.bind("<KeyPress>", self._stop)
        self.flash_window.bind("<Button-1>", self._stop)
        self.flash_window.protocol("WM_DELETE_WINDOW", lambda: self._stop(None))

        self._show_next()

    def _hide_hint(self):
        if self.hint and self.hint.winfo_exists():
            self.hint.place_forget()

    def _show_next(self):
        if not self.running:
            return
        color = random.choice(self.active_colors)
        self.flash_window.configure(bg=color)
        if self.hint and self.hint.winfo_exists():
            self.hint.configure(bg=color)

        lo = self.min_dur.get()
        hi = self.max_dur.get()
        duration = random.randint(lo, hi)
        self.flash_after_id = self.flash_window.after(duration, self._show_next)

    def _stop(self, event):
        self.running = False
        if self.flash_after_id and self.flash_window:
            self.flash_window.after_cancel(self.flash_after_id)
            self.flash_after_id = None
        if self.flash_window:
            self.flash_window.destroy()
            self.flash_window = None

    # ── Run ──────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ReactionTrainer().run()
