import csv
import os
import numpy as np


class PathLoader:
    def __init__(self, filename=None):
        self.filename = filename
        self.path_points = []
        self.current_index = 0

    def load_from_csv(self, filename):
        self.filename = filename
        self.path_points = []

        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return False

        try:
            with open(filename, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    point = {
                        "x": float(row.get("x", 0)),
                        "y": float(row.get("y", 0)),
                        "z": float(row.get("z", 0)),
                        "speed": float(row.get("speed", 1.0)),
                    }
                    self.path_points.append(point)

            print(f"Loaded {len(self.path_points)} points from {filename}")
            return len(self.path_points) > 0

        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False

    def save_to_csv(self, filename, points=None):
        if points is None:
            points = self.path_points

        try:
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["x", "y", "z", "speed"])
                writer.writeheader()
                for point in points:
                    writer.writerow(
                        {
                            "x": point[0]
                            if isinstance(point, (list, tuple))
                            else point.get("x", 0),
                            "y": point[1]
                            if isinstance(point, (list, tuple))
                            else point.get("y", 0),
                            "z": point[2]
                            if isinstance(point, (list, tuple))
                            else point.get("z", 0),
                            "speed": point[3]
                            if isinstance(point, (list, tuple)) and len(point) > 3
                            else 1.0,
                        }
                    )
            print(f"Saved {len(points)} points to {filename}")
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False

    def add_point(self, x, y, z, speed=1.0):
        self.path_points.append({"x": x, "y": y, "z": z, "speed": speed})

    def get_point(self, index):
        if 0 <= index < len(self.path_points):
            return self.path_points[index]
        return None

    def get_next_point(self):
        if self.current_index < len(self.path_points):
            point = self.path_points[self.current_index]
            self.current_index += 1
            return point
        return None

    def reset(self):
        self.current_index = 0

    def get_all_points(self):
        return self.path_points

    def get_point_count(self):
        return len(self.path_points)

    def clear(self):
        self.path_points = []
        self.current_index = 0

    def get_as_array(self):
        return np.array([[p["x"], p["y"], p["z"]] for p in self.path_points])


def create_demo_path(filename="weld_path.csv"):
    loader = PathLoader()
    loader.add_point(0.3, 0.0, 0.9, 0.5)
    loader.add_point(0.35, 0.0, 0.9, 0.5)
    loader.add_point(0.4, 0.0, 0.9, 0.5)
    loader.add_point(0.4, 0.0, 0.85, 0.3)
    loader.add_point(0.35, 0.0, 0.85, 0.3)
    loader.add_point(0.3, 0.0, 0.85, 0.5)
    loader.save_to_csv(filename)
    return loader
