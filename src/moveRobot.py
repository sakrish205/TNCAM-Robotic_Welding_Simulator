import sim
import time
import numpy as np

SPEED_FACTOR = 1.0


def set_speed(speed_percent):
    global SPEED_FACTOR
    SPEED_FACTOR = speed_percent / 100.0


def get_speed():
    return SPEED_FACTOR * 100


def move(clientID, target, destination, speed=1):
    if isinstance(destination, (list, tuple)):
        destination = np.array(destination, dtype=np.float64)

    _, ini_pos = sim.simxGetObjectPosition(
        clientID, target, -1, sim.simx_opmode_streaming
    )
    _, ini_ori = sim.simxGetObjectOrientation(
        clientID, target, -1, sim.simx_opmode_streaming
    )

    time.sleep(0.01)

    _, ini_pos = sim.simxGetObjectPosition(clientID, target, -1, sim.simx_opmode_buffer)
    _, ini_ori = sim.simxGetObjectOrientation(
        clientID, target, -1, sim.simx_opmode_buffer
    )

    for i in range(3):
        if i < len(ini_ori) and i < len(destination) - 3:
            if (abs(destination[i + 3] - ini_ori[i]) > np.pi) and (ini_ori[i] < 0):
                ini_ori[i] = ini_ori[i] + 2 * np.pi
            elif (abs(destination[i + 3] - ini_ori[i]) > np.pi) and (ini_ori[i] > 0):
                ini_ori[i] = ini_ori[i] - 2 * np.pi

    ini_vector = np.concatenate((ini_pos, ini_ori))
    dis_vector = destination - ini_vector

    distance = np.linalg.norm(dis_vector)
    if distance < 0.001:
        return

    samples = max(int(distance * 50), 1)
    effective_speed = speed * SPEED_FACTOR

    current_vector = ini_vector.copy()

    for i in range(samples):
        current_vector = ini_vector + (dis_vector * (i + 1) / samples)

        wait_time = (
            (distance / (effective_speed * samples)) if effective_speed > 0 else 0.01
        )
        time.sleep(max(wait_time, 0.001))

        sim.simxSetObjectPosition(
            clientID, target, -1, current_vector[:3].tolist(), sim.simx_opmode_oneshot
        )

        if len(current_vector) >= 6:
            sim.simxSetObjectOrientation(
                clientID,
                target,
                -1,
                current_vector[3:6].tolist(),
                sim.simx_opmode_oneshot,
            )


def move_to_position(clientID, target_handle, position, speed=1):
    move(clientID, target_handle, position, speed)


def get_joint_handles(clientID, robot_name="IRB4600"):
    joint_handles = []
    for i in range(1, 7):
        name = f"{robot_name}_joint{i}"
        ret, handle = sim.simxGetObjectHandle(clientID, name, sim.simx_opmode_blocking)
        if ret == sim.simx_return_ok:
            joint_handles.append(handle)
    return joint_handles


def set_joint_position(clientID, joint_handle, position, speed=1):
    sim.simxSetJointTargetPosition(
        clientID, joint_handle, position, sim.simx_opmode_oneshot
    )
    time.sleep(0.1 / (speed * SPEED_FACTOR))


def get_joint_position(clientID, joint_handle):
    ret, pos = sim.simxGetJointPosition(clientID, joint_handle, sim.simx_opmode_buffer)
    if ret == sim.simx_return_ok:
        return pos
    return None


def move_joints(clientID, joint_handles, positions, speed=1):
    for handle, pos in zip(joint_handles, positions):
        set_joint_position(clientID, handle, pos, speed)

    time.sleep(0.5 / (speed * SPEED_FACTOR))
