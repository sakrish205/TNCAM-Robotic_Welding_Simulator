import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import threading
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import sim
from src import (
    moveRobot,
    jointControl,
    cameraFollow,
    path_loader,
    data_logger,
    endpoint_tracker,
    safety_controller,
)
from src.gui import open_path_designer


class WeldingSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TNCAM - Robotic Welding Simulator (CoppeliaSim)")
        self.root.geometry("800x650")

        self.clientID = -1
        self.target_handle = -1
        self.joint_controller = None
        self.camera_follower = None
        self.endpoint_tracker = endpoint_tracker.create_endpoint_tracker()
        self.path_loader = path_loader.PathLoader()
        self.logger = None
        self.path_designer = None
        self.safety_controller = None

        self.robot_speed = 50
        self.camera_follow_enabled = False
        self.simulation_running = False

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="wnes")

        title_label = ttk.Label(
            main_frame,
            text="TNCAM - Robotic Welding Control",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        connection_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        connection_frame.grid(row=1, column=0, columnspan=3, sticky="we", pady=5)

        ttk.Button(connection_frame, text="Connect", command=self.connect).grid(
            row=0, column=0, padx=5
        )
        ttk.Button(connection_frame, text="Disconnect", command=self.disconnect).grid(
            row=0, column=1, padx=5
        )
        self.connection_status = tk.Label(
            connection_frame, text="Status: Disconnected", fg="red"
        )
        self.connection_status.grid(row=0, column=2, padx=10)

        control_frame = ttk.LabelFrame(main_frame, text="Robot Control", padding="5")
        control_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=5)

        ttk.Label(control_frame, text="Speed:").grid(row=0, column=0, sticky=tk.W)
        self.speed_slider = ttk.Scale(
            control_frame, from_=10, to=100, orient=tk.HORIZONTAL
        )
        self.speed_slider.set(50)
        self.speed_slider.grid(row=0, column=1, sticky="we", padx=5)
        self.speed_label = tk.Label(control_frame, text="50%")
        self.speed_label.grid(row=0, column=2)
        self.speed_slider.config(command=self.update_speed)

        path_frame = ttk.LabelFrame(main_frame, text="Weld Path", padding="5")
        path_frame.grid(row=3, column=0, columnspan=3, sticky="we", pady=5)

        ttk.Button(
            path_frame, text="Path Designer", command=self.open_path_designer
        ).grid(row=0, column=0, padx=5, sticky="we")

        ttk.Button(path_frame, text="Load CSV", command=self.load_path).grid(
            row=0, column=1, padx=5, sticky="we"
        )

        ttk.Button(path_frame, text="Execute Path", command=self.execute_path).grid(
            row=0, column=2, padx=5, sticky="we"
        )

        self.path_label = tk.Label(path_frame, text="No path loaded")
        self.path_label.grid(row=0, column=4, padx=10)

        logging_frame = ttk.LabelFrame(main_frame, text="Data Logging", padding="5")
        logging_frame.grid(row=4, column=0, columnspan=3, sticky="we", pady=5)

        ttk.Button(
            logging_frame, text="Start Logging", command=self.start_logging
        ).grid(row=0, column=0, padx=5)
        ttk.Button(logging_frame, text="Stop & Save", command=self.stop_logging).grid(
            row=0, column=1, padx=5
        )
        self.logging_status = tk.Label(logging_frame, text="Logging: OFF", fg="gray")
        self.logging_status.grid(row=0, column=2, padx=10)

        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=5, column=0, columnspan=3, sticky="wnes", pady=5)

        self.status_text = tk.Text(status_frame, height=10, width=70)
        self.status_text.grid(row=0, column=0)

        scrollbar = ttk.Scrollbar(
            status_frame, orient=tk.VERTICAL, command=self.status_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.config(yscrollcommand=scrollbar.set)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Auto-load default CSV on startup
        self.auto_load_default_csv()

    def auto_load_default_csv(self):
        # Priority order: path_designer output first, then other files
        default_files = [
            "data/input/weld_path.csv",  # Path designer output (highest priority)
            "weld_path_cube_relative.csv",  # Default cube-relative
            "weld_path.csv",  # Legacy
        ]
        for filename in default_files:
            if self.path_loader.load_from_csv(filename):
                self.path_label.config(
                    text=f"{self.path_loader.get_point_count()} points (auto-loaded)"
                )
                self.log(f"Auto-loaded: {filename}")
                return True
        self.log("No default CSV found - please load a file")
        return False

    def log(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)

    def connect(self):
        try:
            self.clientID = sim.simxStart("127.0.0.1", 19997, True, True, 5000, 5)
            if self.clientID != -1:
                self.connection_status.config(text="Status: Connected", fg="green")
                self.log("Connected to CoppeliaSim on port 19997")

                # Get all objects in scene
                ret, objects = sim.simxGetObjects(
                    self.clientID, sim.sim_handle_all, sim.simx_opmode_blocking
                )
                if ret == sim.simx_return_ok:
                    self.log(f"Scene contains {len(objects)} objects:")
                    for obj in objects:
                        self.log(f"  - {obj}")

                # Check simulation state
                try:
                    ret, sim_state = sim.simxGetIntegerParameter(
                        self.clientID, 2015, sim.simx_opmode_blocking
                    )
                    if ret == sim.simx_return_ok:
                        if sim_state == 0:
                            self.log("WARNING: Simulation is STOPPED!")
                            self.log("Press PLAY in CoppeliaSim to start simulation")
                        elif sim_state == 1:
                            self.log("Simulation is RUNNING")
                        elif sim_state == 2:
                            self.log("Simulation is PAUSED")
                except:
                    pass

                # Try different target names
                target_names = [
                    "Target",
                    "target",
                    "shape",
                    "Shape",
                    "shape0",
                    "shape1",
                ]
                self.target_handle = -1
                for name in target_names:
                    ret, handle = sim.simxGetObjectHandle(
                        self.clientID, name, sim.simx_opmode_blocking
                    )
                    if ret == sim.simx_return_ok:
                        self.target_handle = handle
                        self.log(f"Found target object: {name}")
                        break
                if self.target_handle == -1:
                    self.log("Warning: No target object found")

                # Try joint controller - auto-detect robot name
                detected_robot = jointControl.detect_robot_name(self.clientID)
                self.log(f"Detected robot: {detected_robot}")
                self.joint_controller = jointControl.JointController(
                    self.clientID, detected_robot
                )
                if self.joint_controller.initialize():
                    self.log(f"Found {len(self.joint_controller.joint_handles)} joints")
                    self.log(
                        f"Current joints: {self.joint_controller.get_current_joints_string()}"
                    )
                    # Move to home position on connect
                    self.joint_controller.go_home(speed=0.5)
                    self.log("Moved to home position")
                else:
                    self.log(
                        "Warning: No robot joints found - make sure simulation is RUNNING in CoppeliaSim"
                    )

                # Log endpoint tracker info
                tracker_info = self.endpoint_tracker.get_info()
                self.log(f"Endpoint Tracker: Cube at {tracker_info['cube_center']}")
                self.log(f"  Cube top Z: {tracker_info['cube_top_z']}m")
                self.log(f"  Torch offset: {tracker_info['torch_offset']}m")

                # Try camera follower
                self.camera_follower = cameraFollow.CameraFollower(self.clientID)
                if self.camera_follower.initialize():
                    self.log("Camera follower initialized")
                else:
                    self.log("Note: No Camera object found (optional)")

                # Initialize safety controller with collision detection
                self.safety_controller = safety_controller.SafetyController(
                    self.clientID
                )
                if self.safety_controller.initialize():
                    self.log("Safety controller initialized with collision detection")
                    self.log(
                        f"  Collision objects: {list(self.safety_controller.collision_handles.keys())}"
                    )
                else:
                    self.log("Note: No collision objects found (optional)")

            else:
                messagebox.showerror(
                    "Connection Error", "Failed to connect to CoppeliaSim"
                )
        except Exception as e:
            import traceback

            self.log(f"Error: {e}")
            self.log(traceback.format_exc())
            messagebox.showerror("Error", f"Connection error: {e}")

    def disconnect(self):
        if self.clientID != -1:
            sim.simxFinish(self.clientID)
            self.clientID = -1
            self.connection_status.config(text="Status: Disconnected", fg="red")
            self.log("Disconnected from CoppeliaSim")

    def update_speed(self, value):
        self.robot_speed = int(float(value))
        self.speed_label.config(text=f"{self.robot_speed}%")
        moveRobot.set_speed(self.robot_speed)

    def open_path_designer(self):
        self.path_designer = open_path_designer(self.root, self)
        self.log("Opened Path Designer")

    def load_path_from_designer(self, filename):
        """Load path from file (called by path designer)"""
        if self.path_loader.load_from_csv(filename):
            self.path_label.config(
                text=f"{self.path_loader.get_point_count()} points loaded"
            )
            self.log(f"Loaded path from designer: {filename}")
            # Auto-execute
            self.execute_path()

    def load_path(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            if self.path_loader.load_from_csv(filename):
                self.path_label.config(
                    text=f"{self.path_loader.get_point_count()} points loaded"
                )
                self.log(f"Loaded path: {filename}")

    def execute_path(self):
        if self.clientID == -1:
            self.log("Error: Not connected")
            return

        if self.path_loader.get_point_count() == 0:
            self.log("Error: No path loaded. Use 'Create Demo Path' first")
            return

        self.simulation_running = True
        self.path_loader.reset()

        def run_path():
            # Go home before executing path
            if self.joint_controller:
                self.joint_controller.go_home(speed=0.5)
                self.root.after(0, lambda: self.log("Starting from home position"))

            points = self.path_loader.get_all_points()

            # Transform coordinates using endpoint tracker
            transformed_points, warnings = self.endpoint_tracker.transform_path(points)

            # Show any warnings about points clamped to cube
            if warnings:
                for w in warnings:
                    self.root.after(0, lambda w=w: self.log(f"Warning: {w}"))

            # Turn on welding torch (if signal exists)
            try:
                sim.simxSetIntegerSignal(
                    self.clientID, "welding", 1, sim.simx_opmode_oneshot
                )
                self.root.after(0, lambda: self.log(">>> WELDING TORCH ON <<<"))
            except:
                pass

            self.root.after(
                0,
                lambda: self.log(f"Starting weld... {len(transformed_points)} points"),
            )

            # Generate interpolated points for continuous welding motion
            interpolated_points = []
            interpolation_steps = (
                10  # Number of intermediate points between each waypoint
            )

            for i in range(len(transformed_points) - 1):
                p1 = transformed_points[i]
                p2 = transformed_points[i + 1]

                # Add intermediate points
                for step in range(interpolation_steps):
                    t = step / interpolation_steps
                    interpolated_points.append(
                        {
                            "x": p1["x"] + (p2["x"] - p1["x"]) * t,
                            "y": p1["y"] + (p2["y"] - p1["y"]) * t,
                            "z": p1["z"] + (p2["z"] - p1["z"]) * t,
                            "speed": (p1.get("speed", 0.5) + p2.get("speed", 0.5)) / 2,
                        }
                    )

            # Add final point
            interpolated_points.append(transformed_points[-1])

            # Execute interpolated path
            for i, point in enumerate(interpolated_points):
                if not self.simulation_running:
                    break

                try:
                    # Use transformed world coordinates - move Target object
                    pos = [point["x"], point["y"], point["z"]]
                    combined_speed = point.get("speed", 0.5) * moveRobot.SPEED_FACTOR

                    if self.target_handle != -1:
                        ret = sim.simxSetObjectPosition(
                            self.clientID,
                            self.target_handle,
                            -1,
                            pos,
                            sim.simx_opmode_oneshot,
                        )

                        ori = [0, 0, 0]
                        sim.simxSetObjectOrientation(
                            self.clientID,
                            self.target_handle,
                            -1,
                            ori,
                            sim.simx_opmode_oneshot,
                        )

                    # Move robot joints using IK (numerical inverse kinematics)
                    if (
                        self.joint_controller
                        and len(self.joint_controller.joint_handles) > 0
                    ):
                        # Use IK to calculate joint angles for target position
                        self.joint_controller.move_to_ik_target(
                            pos[0], pos[1], pos[2], combined_speed
                        )
                        self.joint_controller.move_to_ik_target(
                            pos[0], pos[1], pos[2], combined_speed
                        )

                    # Check for collision before continuing
                    if self.safety_controller:
                        collision_detected, collision_name = (
                            self.safety_controller.check_collision()
                        )
                        if collision_detected:
                            self.root.after(
                                0,
                                lambda n=collision_name: self.log(
                                    f"COLLISION DETECTED: {n} - Stopping!"
                                ),
                            )
                            self.simulation_running = False
                            break

                    # Short wait for smooth continuous motion
                    wait_time = 0.05 / max(combined_speed, 0.1)
                    time.sleep(wait_time)

                    # Log progress every 10 points
                    if i % 10 == 0:
                        self.root.after(
                            0,
                            lambda n=i, p=pos: self.log(
                                f"Welding... X={p[0]:.3f}, Y={p[1]:.3f}, Z={p[2]:.3f}"
                            ),
                        )
                except Exception as e:
                    self.root.after(0, lambda e=e: self.log(f"Error: {e}"))

            # Turn off welding torch
            try:
                sim.simxSetIntegerSignal(
                    self.clientID, "welding", 0, sim.simx_opmode_oneshot
                )
                self.root.after(0, lambda: self.log(">>> WELDING TORCH OFF <<<"))
            except:
                pass

            self.root.after(0, lambda: self.log("Weld complete!"))

            # Return home after welding
            if self.joint_controller:
                self.joint_controller.go_home(speed=0.5)
                self.root.after(0, lambda: self.log("Returned to home position"))

            self.root.after(0, lambda: self.set_simulation_running(False))

        thread = threading.Thread(target=run_path)
        thread.start()

    def set_simulation_running(self, running):
        self.simulation_running = running

    def start_logging(self):
        self.logger = data_logger.create_logger()
        self.logger.start()
        self.logging_status.config(text="Logging: ON", fg="green")
        self.log("Data logging started")

    def stop_logging(self):
        if self.logger:
            self.logger.save()
            self.logger.export_kpis()
            self.logging_status.config(text="Logging: OFF", fg="gray")
            self.log("Data logging saved")


def main():
    root = tk.Tk()
    app = WeldingSimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
