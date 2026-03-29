import csv
import os
import time
import numpy as np
from datetime import datetime


class DataLogger:
    def __init__(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"welding_log_{timestamp}.csv"

        self.filename = filename
        self.data = []
        self.start_time = None
        self.headers = [
            "time",
            "joint1",
            "joint2",
            "joint3",
            "joint4",
            "joint5",
            "joint6",
            "x",
            "y",
            "z",
            "speed",
            "safety_state",
        ]

    def start(self):
        self.start_time = time.time()
        self.data = []
        print(f"Logging started: {self.filename}")

    def log(
        self,
        joint_positions=None,
        end_effector_pos=None,
        speed=1.0,
        safety_state="NORMAL",
    ):
        if self.start_time is None:
            self.start()

        elapsed = time.time() - self.start_time

        row = {
            "time": round(elapsed, 3),
            "joint1": joint_positions[0]
            if joint_positions and len(joint_positions) > 0
            else 0,
            "joint2": joint_positions[1]
            if joint_positions and len(joint_positions) > 1
            else 0,
            "joint3": joint_positions[2]
            if joint_positions and len(joint_positions) > 2
            else 0,
            "joint4": joint_positions[3]
            if joint_positions and len(joint_positions) > 3
            else 0,
            "joint5": joint_positions[4]
            if joint_positions and len(joint_positions) > 4
            else 0,
            "joint6": joint_positions[5]
            if joint_positions and len(joint_positions) > 5
            else 0,
            "x": end_effector_pos[0] if end_effector_pos else 0,
            "y": end_effector_pos[1] if end_effector_pos else 0,
            "z": end_effector_pos[2] if end_effector_pos else 0,
            "speed": speed,
            "safety_state": safety_state,
        }

        self.data.append(row)

    def save(self):
        if not self.data:
            print("No data to save")
            return False

        try:
            with open(self.filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(self.data)
            print(f"Log saved: {self.filename} ({len(self.data)} rows)")
            return True
        except Exception as e:
            print(f"Error saving log: {e}")
            return False

    def get_statistics(self):
        if not self.data:
            return {}

        times = [d["time"] for d in self.data]
        speeds = [d["speed"] for d in self.data]

        stats = {
            "duration": max(times) - min(times) if times else 0,
            "avg_speed": np.mean(speeds) if speeds else 0,
            "max_speed": max(speeds) if speeds else 0,
            "min_speed": min(speeds) if speeds else 0,
            "total_points": len(self.data),
        }

        return stats

    def export_kpis(self, filename=None):
        if filename is None:
            filename = self.filename.replace(".csv", "_kpis.txt")

        stats = self.get_statistics()

        try:
            with open(filename, "w") as f:
                f.write("=== Welding Session KPIs ===\n\n")
                f.write(f"Duration: {stats['duration']:.2f} seconds\n")
                f.write(f"Average Speed: {stats['avg_speed'] * 100:.1f}%\n")
                f.write(f"Max Speed: {stats['max_speed'] * 100:.1f}%\n")
                f.write(f"Min Speed: {stats['min_speed'] * 100:.1f}%\n")
                f.write(f"Data Points: {stats['total_points']}\n")
            print(f"KPIs exported: {filename}")
            return True
        except Exception as e:
            print(f"Error exporting KPIs: {e}")
            return False


def create_logger(filename=None):
    return DataLogger(filename)
