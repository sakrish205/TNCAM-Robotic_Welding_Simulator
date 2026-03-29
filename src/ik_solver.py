import numpy as np


def get_end_effector_position(joint_angles):
    q = joint_angles

    def FK(theta, alpha, a, d):
        theta_rad = np.deg2rad(theta)
        alpha_rad = np.deg2rad(alpha)
        return np.array(
            [
                [
                    np.cos(theta_rad),
                    -np.sin(theta_rad) * np.cos(alpha_rad),
                    np.sin(theta_rad) * np.sin(alpha_rad),
                    a * np.cos(theta_rad),
                ],
                [
                    np.sin(theta_rad),
                    np.cos(theta_rad) * np.cos(alpha_rad),
                    -np.cos(theta_rad) * np.sin(alpha_rad),
                    a * np.sin(theta_rad),
                ],
                [0, np.sin(alpha_rad), np.cos(alpha_rad), d],
                [0, 0, 0, 1],
            ]
        )

    T1 = FK(np.degrees(q[0]), -90, 0.510, 0.690)
    T2 = FK(np.degrees(q[1]) - 90, 0, 0.900, 0)
    T3 = FK(np.degrees(q[2]), -90, 0.175, 0)
    T4 = FK(np.degrees(q[3]), 90, 0, 0.960)
    T5 = FK(np.degrees(q[4]) + 180, 90, 0, 0)
    T6 = FK(np.degrees(q[5]), 0, 0, 0.365)

    T = T1 @ T2 @ T3 @ T4 @ T5 @ T6
    return T[:3, 3]


class IKSolver:
    def __init__(self):
        self.current_joints = [0.0] * 6
        # Calibrated home position - torch ON cube surface
        self.default_initial = [-0.038863, 0.160718, 0.359108, 0.000310, -0.074666, 0.0]

    def set_current_joints(self, joints):
        if joints and len(joints) >= 6:
            self.current_joints = list(joints[:6])

    def calculate_ik(self, x, y, z, initial_q=None):
        if initial_q is None:
            initial_q = self.default_initial

        q = np.array(initial_q, dtype=float)
        target = np.array([x, y, z])

        for _ in range(200):
            pos = get_end_effector_position(q.tolist())
            error = target - pos

            if np.linalg.norm(error) < 0.005:
                return q.tolist()

            delta = 0.0001
            J = np.zeros((3, 6))
            pos_current = get_end_effector_position(q.tolist())
            for i in range(6):
                q_test = q.copy()
                q_test[i] += delta
                pos_test = get_end_effector_position(q_test.tolist())
                J[:, i] = (pos_test - pos_current) / delta

            try:
                q += 0.6 * J.T @ np.linalg.inv(J @ J.T + 0.001 * np.eye(3)) @ error
            except:
                q += 0.1 * J.T @ error

            q = np.clip(q, -np.pi * 2, np.pi * 2)

        return q.tolist()

    def forward_kinematics(self, joint_angles):
        return get_end_effector_position(joint_angles)

    def get_end_effector_position(self, joint_angles):
        return get_end_effector_position(joint_angles)


def create_ik_solver():
    return IKSolver()


if __name__ == "__main__":
    print("IK Solver - FINAL TEST")
    print("=" * 50)

    ik = IKSolver()

    test_positions = [
        (0.050, 1.625, 1.075),
        (0.100, 1.625, 1.075),
        (0.050, 1.700, 1.075),
    ]

    for x, y, z in test_positions:
        result = ik.calculate_ik(x, y, z)
        pos = ik.get_end_effector_position(result)
        error = np.linalg.norm(np.array([x, y, z]) - pos)

        print(f"\nTarget: ({x}, {y}, {z})")
        print(f"Result: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
        print(f"Error: {error * 1000:.1f}mm")
        print(f"Joints: {[f'{np.degrees(j):.1f}°' for j in result]}")
