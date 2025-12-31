import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import importlib

# app.py
# Simple desktop app to input target values (start/end + optional mid points),
# submit to a backend (dummy fallback) and display an interpolated graph.

# Try to import real backend.py; if missing, use an internal dummy implementation.
try:
    backend = importlib.import_module("backend")
    print("Imported backend.py successfully.")
    has_backend = True
except Exception:
    has_backend = False

    class backend:
        @staticmethod
        def process(values):
            # Dummy: interpolate values and add light random variance
            n = len(values)
            x_out = np.linspace(0, n - 1, 200)
            y_base = np.interp(x_out, np.arange(n), np.array(values))
            # variance proportional to range
            rng = max(1.0, (max(values) - min(values))) if n > 1 else 1.0
            noise = np.random.normal(scale=0.05 * rng, size=x_out.shape)
            y_out = y_base + noise
            return x_out, y_out


class InterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interpolation with Variance")
        self.entries = []  # list of (label_widget, entry_widget)
        self.current_values = []  # list of numeric values from backend
        self.selected_point = None  # index of selected point for editing
        self._build_ui()
        self._init_plot()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="both", expand=True)

        # Inputs frame
        self.inputs_frame = ttk.LabelFrame(frm, text="Target Values", padding=8)
        self.inputs_frame.pack(side="top", fill="x", expand=False)

        # Start and End fields
        self._add_entry("Start")
        self._add_entry("End")

        # Controls
        controls = ttk.Frame(frm)
        controls.pack(side="top", fill="x", pady=(8, 0))

        add_btn = ttk.Button(controls, text="Add Field", command=self.add_field)
        add_btn.pack(side="left")

        submit_btn = ttk.Button(controls, text="Submit", command=self.submit)
        submit_btn.pack(side="left", padx=(8, 0))

        clear_btn = ttk.Button(controls, text="Clear", command=self.clear_all)
        clear_btn.pack(side="left", padx=(8, 0))

        # Info label for editing
        self.info_label = ttk.Label(controls, text="Click points on graph to edit", foreground="gray")
        self.info_label.pack(side="left", padx=(20, 0))

    def _add_entry(self, label_text, before_end=False):
        # Insert before the last entry if before_end=True, otherwise append
        if before_end and len(self.entries) >= 1:
            insert_index = len(self.entries) - 1
        else:
            insert_index = len(self.entries)

        # create widgets
        label = ttk.Label(self.inputs_frame, text=f"{label_text}:")
        entry = ttk.Entry(self.inputs_frame, width=12)

        # grid placement: simple vertical stack
        # First, shift down widgets below insert index
        for i in range(insert_index, len(self.entries)):
            lbl, ent = self.entries[i]
            lbl.grid_configure(row=i + 1, column=0, sticky="w", pady=2)
            ent.grid_configure(row=i + 1, column=1, sticky="w", pady=2)

        label.grid(row=insert_index, column=0, sticky="w", pady=2, padx=(0, 6))
        entry.grid(row=insert_index, column=1, sticky="w", pady=2)

        self.entries.insert(insert_index, (label, entry))

        # Pre-fill placeholder for convenience
        if label_text == "Start":
            entry.insert(0, "0")
        elif label_text == "End" and entry.get() == "":
            entry.insert(0, "1")

    def add_field(self):
        # New field goes between start and end (i.e., before last)
        idx = len(self.entries) - 1
        name = f"Point {idx}"
        self._add_entry(name, before_end=True)

    def _init_plot(self):
        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Value")

        canvas_frame = ttk.LabelFrame(self.root, text="Plot", padding=6)
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
        
        # Connect click event for point editing
        self.canvas.mpl_connect("button_press_event", self.on_plot_click)

    def _clear_plot(self):
        self.ax.cla()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Value")
        self.canvas.draw()

    def on_plot_click(self, event):
        """Handle clicks on plot points for editing"""
        if event.inaxes != self.ax or not self.current_values:
            return
        
        x_pts = np.arange(len(self.current_values))
        clicked_x, clicked_y = event.xdata, event.ydata
        
        # Find nearest point
        distances = np.sqrt((x_pts - clicked_x) ** 2 + 
                           (np.array(self.current_values) - clicked_y) ** 2)
        nearest_idx = np.argmin(distances)
        
        # Only select if click is close enough
        if distances[nearest_idx] < 0.3:
            self.edit_point(nearest_idx)

    def edit_point(self, idx):
        """Open dialog to edit a specific point"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Point {idx}")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text=f"Edit value for point {idx}:").pack(pady=10)
        
        entry = ttk.Entry(dialog, width=15)
        entry.pack(pady=5)
        entry.insert(0, str(self.current_values[idx]))
        entry.focus()
        
        def save():
            try:
                new_val = float(entry.get().strip())
                self.current_values[idx] = new_val
                # Update the input field
                if idx < len(self.entries):
                    _, ent = self.entries[idx]
                    ent.delete(0, tk.END)
                    ent.insert(0, str(new_val))
                dialog.destroy()
                self.submit()  # Replot
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter a numeric value.")
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=5)

    def submit(self):
        try:
            values = []
            for _, ent in self.entries:
                txt = ent.get().strip()
                if txt == "":
                    raise ValueError("All fields must be filled.")
                val = float(txt)
                values.append(val)
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Please enter numeric values in all fields.\n{e}")
            return

        if len(values) < 2:
            messagebox.showerror("Not enough points", "Please provide at least start and end values.")
            return

        self.current_values = values

        # Call backend (real or dummy)
        try:
            x_out, y_out = backend.process(values)
            print(f"Backend returned {len(x_out)} points.")
        except Exception as e:
            messagebox.showerror("Backend error", f"Backend processing failed: {e}")
            return

        # Plot results
        self._clear_plot()
        self.ax.plot(x_out, y_out, label="Interpolated (backend)")
        # overlay original points
        x_pts = np.arange(len(values))
        self.ax.scatter(x_pts, values, color="red", zorder=5, label="Targets (click to edit)")
        self.ax.legend()
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def clear_all(self):
        # remove all entries and recreate start/end
        for lbl, ent in self.entries:
            lbl.destroy()
            ent.destroy()
        self.entries = []
        self.current_values = []
        self._add_entry("Start")
        self._add_entry("End")
        self._clear_plot()


def main():
    root = tk.Tk()
    InterpolationApp(root)
    root.geometry("700x500")
    # Inform whether a real backend.py was loaded
    if has_backend:
        print("Using backend.py")
    else:
        print("No backend.py found — using internal dummy backend.")
    root.mainloop()


if __name__ == "__main__":
    main()