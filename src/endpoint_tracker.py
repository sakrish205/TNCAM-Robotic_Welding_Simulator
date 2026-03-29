import numpy as np


class EndpointTracker:
    def __init__(self):
        self.cube_center = np.array([0.050, 1.625, 1.000])
        self.cube_top_z = 1.075
        self.cube_size = 0.15
        self.robot_base = np.array([0, 0, 0.0975])
        self.torch_offset = np.array([0, 0, -0.01])
        self.torch_length = 0.23
        self.torch_orientation = [np.pi, 0, 0]

        # Cube boundaries (vertices)
        self.cube_x_min = -0.025
        self.cube_x_max = 0.125
        self.cube_y_min = 1.550
        self.cube_y_max = 1.700
        self.cube_z = 1.075  # Top surface

    def is_within_cube(self, x, y, z=None):
        """Check if point is within cube boundaries"""
        half_size = self.cube_size / 2

        # Check X and Y bounds
        x_valid = self.cube_x_min <= x <= self.cube_x_max
        y_valid = self.cube_y_min <= y <= self.cube_y_max

        if z is not None:
            # Check Z is at cube top surface
            z_valid = abs(z - self.cube_top_z) < 0.01
            return x_valid and y_valid and z_valid

        return x_valid and y_valid

    def clamp_to_cube(self, x, y, z=None):
        """Clamp coordinates to be within cube boundaries"""
        x_clamped = max(self.cube_x_min, min(self.cube_x_max, x))
        y_clamped = max(self.cube_y_min, min(self.cube_y_max, y))

        if z is not None:
            return x_clamped, y_clamped, self.cube_top_z
        return x_clamped, y_clamped

    def set_cube_position(self, x, y, z):
        self.cube_center = np.array([x, y, z])
        self.cube_top_z = z + 0.075

    def set_robot_base(self, x, y, z):
        self.robot_base = np.array([x, y, z])

    def set_torch_offset(self, offset):
        if isinstance(offset, (list, tuple)):
            self.torch_offset = np.array(offset)
        else:
            self.torch_offset = np.array([0, 0, offset])

    def set_torch_length(self, length):
        self.torch_length = length

    def transform_relative_to_world(self, rel_x, rel_y, rel_z):
        # Target cube TOP surface, not center
        # Cube center: (0.050, 1.625, 1.000), Top surface: Z = 1.075
        world_x = self.cube_center[0] + rel_x
        world_y = self.cube_center[1] + rel_y
        world_z = self.cube_top_z + rel_z  # Use TOP surface Z
        return [world_x, world_y, world_z]

    def transform_to_world(self, rel_x, rel_y, rel_z):
        return self.transform_relative_to_world(rel_x, rel_y, rel_z)

    def apply_torch_offset(self, x, y, z):
        # IK solver already includes torch length (230mm), no additional offset needed
        return [x, y, z]

    def get_cube_relative_target(self, rel_x, rel_y, rel_z):
        world_pos = self.transform_to_world(rel_x, rel_y, rel_z)
        return world_pos

    def transform_path(self, path_points):
        transformed = []
        warnings = []

        for i, point in enumerate(path_points):
            x = point.get("x", 0)
            y = point.get("y", 0)
            z = point.get("z", 0)

            # Convert relative to world coordinates
            world_x = self.cube_center[0] + x
            world_y = self.cube_center[1] + y
            world_z = self.cube_top_z + z

            # Validate within cube boundaries
            if not self.is_within_cube(world_x, world_y, world_z):
                orig_x, orig_y = world_x, world_y
                world_x, world_y, world_z = self.clamp_to_cube(
                    world_x, world_y, world_z
                )
                warnings.append(
                    f"Point {i + 1}: ({orig_x:.3f}, {orig_y:.3f}) clamped to ({world_x:.3f}, {world_y:.3f})"
                )

            # IK solver includes torch length, no extra offset needed
            transformed.append(
                {
                    "x": world_x,
                    "y": world_y,
                    "z": world_z,
                    "speed": point.get("speed", 1.0),
                }
            )

        return transformed, warnings

    def transform_array(self, points):
        transformed = []
        for point in points:
            x, y, z = point[0], point[1], point[2]
            world_pos = self.transform_relative_to_world(x, y, z)
            torch_adjusted = self.apply_torch_offset(
                world_pos[0], world_pos[1], world_pos[2]
            )
            speed = point[3] if len(point) > 3 else 1.0
            transformed.append(
                [torch_adjusted[0], torch_adjusted[1], torch_adjusted[2], speed]
            )
        return np.array(transformed)

    def get_info(self):
        return {
            "cube_center": self.cube_center.tolist(),
            "cube_top_z": self.cube_top_z,
            "robot_base": self.robot_base.tolist(),
            "torch_offset": self.torch_offset.tolist(),
            "torch_length": self.torch_length,
            "description": "Transforms cube-relative coordinates to world coordinates with IK support",
        }


def create_endpoint_tracker():
    return EndpointTracker()


if __name__ == "__main__":
    tracker = EndpointTracker()

    print("Endpoint Tracker Test")
    print("=" * 50)
    print(f"Cube center: {tracker.cube_center}")
    print(f"Cube top Z: {tracker.cube_top_z}")
    print(f"Torch offset: {tracker.torch_offset}")
    print()

    test_points = [
        {"x": 0, "y": 0, "z": 0, "speed": 0.5},
        {"x": 0.02, "y": 0, "z": 0, "speed": 0.5},
        {"x": 0.04, "y": 0, "z": 0, "speed": 0.5},
    ]

    transformed = tracker.transform_path(test_points)
    for i, pt in enumerate(transformed):
        print(f"Point {i + 1}: X={pt['x']:.3f}, Y={pt['y']:.3f}, Z={pt['z']:.3f}")
