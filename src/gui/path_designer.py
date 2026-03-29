import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src import path_loader


class PathDesigner(tk.Toplevel):
    def __init__(self, parent=None, main_app=None):
        super().__init__(parent)
        self.title("2D Weld Path Designer")
        self.geometry("600x450")

        self.parent = parent
        self.main_app = main_app
        self.points = []
        self.cube_size = 0.15
        self.canvas_size = 300
        self.scale = self.canvas_size / self.cube_size

        # Cube center in world coordinates (for canvas display)
        self.cube_center_x = 0.050
        self.cube_center_y = 1.625
        # Relative Z-height (0 = cube top surface)
        self.z_height = 0.0  # Relative to cube top (will be added to cube_top_z=1.075)

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=0, column=0, padx=5, pady=5)

        self.canvas = tk.Canvas(
            canvas_frame, width=self.canvas_size, height=self.canvas_size, bg="white"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.draw_grid()

        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        controls_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        ttk.Label(controls_frame, text="Z: Fixed at cube top (0.000m)").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=5
        )

        ttk.Button(controls_frame, text="Clear All", command=self.clear_points).grid(
            row=1, column=0, pady=5, sticky=tk.W + tk.E
        )
        ttk.Button(controls_frame, text="Undo Last", command=self.undo_point).grid(
            row=2, column=0, pady=5, sticky=tk.W + tk.E
        )
        ttk.Button(controls_frame, text="Export CSV", command=self.export_csv).grid(
            row=3, column=0, pady=5, sticky=tk.W + tk.E
        )

        # Execute Path button
        ttk.Button(controls_frame, text="Execute Path", command=self.run_path).grid(
            row=4, column=0, pady=15, sticky=tk.W + tk.E
        )

        points_frame = ttk.LabelFrame(main_frame, text="Points", padding="5")
        points_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        self.points_listbox = tk.Listbox(points_frame, height=10, width=60)
        self.points_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            points_frame, orient=tk.VERTICAL, command=self.points_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.points_listbox.config(yscrollcommand=scrollbar.set)

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Label(
            info_frame, text="Canvas: 300x300px = 0.15m x 0.15m (cube top)"
        ).pack()
        ttk.Label(
            info_frame, text="Click to add points | Z-height relative to cube surface"
        ).pack()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def draw_grid(self):
        self.canvas.delete("all")

        margin = 20
        grid_size = self.canvas_size - 2 * margin

        for i in range(5):
            x = margin + i * (grid_size / 4)
            self.canvas.create_line(
                x, margin, x, self.canvas_size - margin, fill="#ddd"
            )
            self.canvas.create_line(
                margin, x, self.canvas_size - margin, x, fill="#ddd"
            )

        self.canvas.create_rectangle(
            margin,
            margin,
            self.canvas_size - margin,
            self.canvas_size - margin,
            outline="blue",
            width=2,
        )

        cx = self.canvas_size / 2
        cy = self.canvas_size / 2
        self.canvas.create_oval(
            cx - 5, cy - 5, cx + 5, cy + 5, fill="red", outline="red"
        )

        for point in self.points:
            # Convert relative coords back to absolute for display
            abs_x = self.cube_center_x + point["x"]
            abs_y = self.cube_center_y + point["y"]
            px, py = self.world_to_canvas(abs_x, abs_y)
            self.canvas.create_oval(
                px - 4, py - 4, px + 4, py + 4, fill="green", outline="darkgreen"
            )

        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                # Convert relative coords back to absolute for display
                p1_abs = (
                    self.cube_center_x + self.points[i]["x"],
                    self.cube_center_y + self.points[i]["y"],
                )
                p2_abs = (
                    self.cube_center_x + self.points[i + 1]["x"],
                    self.cube_center_y + self.points[i + 1]["y"],
                )
                p1 = self.world_to_canvas(p1_abs[0], p1_abs[1])
                p2 = self.world_to_canvas(p2_abs[0], p2_abs[1])
                self.canvas.create_line(
                    p1[0], p1[1], p2[0], p2[1], fill="blue", width=2
                )

    def world_to_canvas(self, wx, wy):
        margin = 20
        cx = (wx - self.cube_center_x + self.cube_size / 2) * self.scale + margin
        cy = (wy - self.cube_center_y + self.cube_size / 2) * self.scale + margin
        return cx, cy

    def canvas_to_world(self, cx, cy):
        margin = 20
        wx = (cx - margin) / self.scale - self.cube_size / 2 + self.cube_center_x
        wy = (cy - margin) / self.scale - self.cube_size / 2 + self.cube_center_y
        return wx, wy

    def on_canvas_click(self, event):
        wx, wy = self.canvas_to_world(event.x, event.y)

        half_size = self.cube_size / 2
        if (
            abs(wx - self.cube_center_x) <= half_size
            and abs(wy - self.cube_center_y) <= half_size
        ):
            # Use relative coords (relative to cube center)
            # Z is always 0 (top face of cube)
            point = {
                "x": wx - self.cube_center_x,
                "y": wy - self.cube_center_y,
                "z": 0.0,  # Always on cube top face
                "speed": 0.5,
            }
            self.points.append(point)
            self.update_points_list()
            self.draw_grid()
        else:
            messagebox.showwarning(
                "Out of Bounds", "Point must be within cube area (0.15m x 0.15m)"
            )

    def update_z_label(self, value):
        self.z_height = float(value)
        self.z_value_label.config(text=f"{self.z_height:.3f}m")

    def update_z(self, value):
        self.z_height = float(value)

    def run_path(self):
        if not self.points:
            messagebox.showwarning("No Points", "Add some points first!")
            return

        # Ensure directory exists
        data_dir = os.path.join(project_root, "data", "input")
        os.makedirs(data_dir, exist_ok=True)

        default_path = os.path.join(data_dir, "weld_path.csv")
        loader = path_loader.PathLoader()
        for p in self.points:
            loader.add_point(p["x"], p["y"], p["z"], p.get("speed", 0.5))
        loader.save_to_csv(default_path)

        messagebox.showinfo(
            "Path Saved", f"Saved to: {default_path}\nPoints: {len(self.points)}"
        )

        if hasattr(self, "main_app") and self.main_app:
            try:
                self.main_app.load_path_from_designer(default_path)
            except Exception as e:
                print(f"Error calling main_app: {e}")

        self.destroy()

    def update_points_list(self):
        self.points_listbox.delete(0, tk.END)
        cube_top_z = 1.075  # Absolute cube top Z
        for i, p in enumerate(self.points):
            # Show relative coords (for CSV) and world coords
            world_x = self.cube_center_x + p["x"]
            world_y = self.cube_center_y + p["y"]
            world_z = cube_top_z + p["z"]
            self.points_listbox.insert(
                tk.END,
                f"P{i + 1}: X={p['x']:.4f}, Y={p['y']:.4f}, Z={p['z']:+.3f} → W:({world_x:.3f},{world_y:.3f},{world_z:.3f})",
            )

    def clear_points(self):
        self.points = []
        self.update_points_list()
        self.draw_grid()

    def undo_point(self):
        if self.points:
            self.points.pop()
            self.update_points_list()
            self.draw_grid()

    def export_csv(self):
        if not self.points:
            messagebox.showwarning("No Points", "Add some points first!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.join(project_root, "data", "input"),
        )

        if filename:
            loader = path_loader.PathLoader()
            for p in self.points:
                loader.add_point(p["x"], p["y"], p["z"], p.get("speed", 0.5))
            loader.save_to_csv(filename)
            messagebox.showinfo(
                "Success", f"Exported {len(self.points)} points to {filename}"
            )

    def import_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.join(project_root, "data", "input"),
        )

        if filename:
            loader = path_loader.PathLoader()
            if loader.load_from_csv(filename):
                self.points = loader.get_all_points()
                self.update_points_list()
                self.draw_grid()
                messagebox.showinfo("Success", f"Loaded {len(self.points)} points")
            else:
                messagebox.showerror("Error", "Failed to load CSV")

    def get_points(self):
        return self.points


def open_path_designer(parent=None, main_app=None):
    designer = PathDesigner(parent, main_app)
    return designer


if __name__ == "__main__":
    root = tk.Tk()
    app = PathDesigner(root)
    root.mainloop()
