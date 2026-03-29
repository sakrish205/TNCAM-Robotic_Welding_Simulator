import json
import os


class WorkspaceLayout:
    def __init__(self):
        self.layout = {
            "robot": {
                "name": "IRB4600",
                "position": [0, 0, 0.0975],
                "description": "Robot base - height 0.0975m from ground",
                "joint_names": [
                    "IRB4600_joint1",
                    "IRB4600_joint2",
                    "IRB4600_joint3",
                    "IRB4600_joint4",
                    "IRB4600_joint5",
                    "IRB4600_joint6",
                ],
            },
            "torch": {
                "name": "WeldingTorch",
                "length": 0.23,
                "offset": [0, 0, -0.01],
                "description": "Torch length 0.23m, offset 0.01m above surface",
            },
            "table": {
                "name": "Table",
                "position": [0.025, 2.200, 0],
                "dimensions": [1.0, 1.0, 1.0],
                "description": "Work table - top at 1.000m",
            },
            "cube": {
                "name": "Cube",
                "position": [0.050, 1.625, 1.000],
                "dimensions": [0.15, 0.15, 0.15],
                "top_face_z": 1.075,
                "vertices": {
                    "V1": [-0.025, 1.55, 1.075],
                    "V2": [0.125, 1.55, 1.075],
                    "V3": [0.125, 1.70, 1.075],
                    "V4": [-0.025, 1.70, 1.075],
                },
                "description": "Welding workpiece - center at (0.050, 1.625, 1.000), top at Z=1.075",
            },
            "human": {
                "name": "Human",
                "position": [1.2, 0, 0.85],
                "dimensions": [0.5, 0.5, 1.7],
                "description": "Human obstacle",
            },
            "safety_zones": {
                "red_zone": 0.5,
                "yellow_zone": 1.0,
                "description": "Safety distances from robot",
            },
        }

        self.config_file = None

    def get(self, key):
        return self.layout.get(key)

    def set_position(self, key, position):
        if key in self.layout:
            self.layout[key]["position"] = position
            return True
        return False

    def get_position(self, key):
        if key in self.layout:
            return self.layout[key].get("position")
        return None

    def get_dimensions(self, key):
        if key in self.layout:
            return self.layout[key].get("dimensions")
        return None

    def get_top_surface_z(self, key):
        pos = self.get_position(key)
        dim = self.get_dimensions(key)

        if pos and dim:
            return pos[2] + dim[2] / 2
        return None

    def save(self, filepath=None):
        if filepath is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(project_root, "data", "workspace_layout.json")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(self.layout, f, indent=4)

        self.config_file = filepath
        return filepath

    def load(self, filepath):
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as f:
            self.layout = json.load(f)

        self.config_file = filepath
        return True

    def get_all_positions(self):
        positions = {}
        for key, value in self.layout.items():
            if "position" in value:
                positions[key] = value["position"]
        return positions

    def print_layout(self):
        print("=== Workspace Layout ===")
        print(f"\nRobot: {self.layout['robot']['position']}")
        print(
            f"Table: {self.layout['table']['position']} (dims: {self.layout['table']['dimensions']})"
        )
        print(
            f"Cube: {self.layout['cube']['position']} (dims: {self.layout['cube']['dimensions']}, top: {self.get_top_surface_z('cube')}m)"
        )
        print(f"Human: {self.layout['human']['position']}")
        print(f"\nSafety Zones:")
        print(f"  Red: {self.layout['safety_zones']['red_zone']}m")
        print(f"  Yellow: {self.layout['safety_zones']['yellow_zone']}m")

    def get_cube_top_z(self):
        return self.get_top_surface_z("cube")

    def get_table_top_z(self):
        return self.get_top_surface_z("table")

    def get_robot_base(self):
        if "robot" in self.layout:
            return self.layout["robot"].get("position", [0, 0, 0])
        return [0, 0, 0]

    def get_torch_offset(self):
        if "torch" in self.layout:
            return self.layout["torch"].get("offset", [0, 0, -0.01])
        return [0, 0, -0.01]

    def get_torch_length(self):
        if "torch" in self.layout:
            return self.layout["torch"].get("length", 0.23)
        return 0.23

    def get_joint_names(self):
        if "robot" in self.layout:
            return self.layout["robot"].get("joint_names", [])
        return []


def create_default_layout():
    return WorkspaceLayout()


def load_layout(filepath=None):
    layout = WorkspaceLayout()
    if filepath and os.path.exists(filepath):
        layout.load(filepath)
    return layout
