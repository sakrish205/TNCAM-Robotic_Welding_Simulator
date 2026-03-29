import sim
import time


class CoppeliaClient:
    def __init__(self, port=19997, timeout=5000):
        self.port = port
        self.timeout = timeout
        self.clientID = -1
        self.connected = False

    def connect(self):
        sim.simxFinish(-1)
        self.clientID = sim.simxStart(
            "127.0.0.1", self.port, True, True, self.timeout, 5
        )

        if self.clientID != -1:
            self.connected = True
            print(f"Connected to CoppeliaSim on port {self.port}")
            time.sleep(0.5)
            return self.clientID
        else:
            print(f"Failed to connect on port {self.port}")
            return -1

    def disconnect(self):
        if self.connected:
            sim.simxFinish(self.clientID)
            self.connected = False
            print("Disconnected from CoppeliaSim")

    def get_handle(self, name):
        if not self.connected:
            return -1, None
        return sim.simxGetObjectHandle(self.clientID, name, sim.simx_opmode_blocking)

    def get_position(self, handle, relative_to=-1):
        if not self.connected:
            return None
        return sim.simxGetObjectPosition(
            self.clientID, handle, relative_to, sim.simx_opmode_streaming
        )

    def set_position(self, handle, position, relative_to=-1):
        if not self.connected:
            return
        sim.simxSetObjectPosition(
            self.clientID, handle, relative_to, position, sim.simx_opmode_oneshot
        )

    def get_orientation(self, handle, relative_to=-1):
        if not self.connected:
            return None
        return sim.simxGetObjectOrientation(
            self.clientID, handle, relative_to, sim.simx_opmode_streaming
        )

    def set_orientation(self, handle, orientation, relative_to=-1):
        if not self.connected:
            return
        sim.simxSetObjectOrientation(
            self.clientID, handle, relative_to, orientation, sim.simx_opmode_oneshot
        )

    def is_connected(self):
        return self.connected and sim.simxGetConnectionId(self.clientID) != -1


_client = None


def get_client(port=19997):
    global _client
    if _client is None:
        _client = CoppeliaClient(port)
        _client.connect()
    return _client


def disconnect():
    global _client
    if _client:
        _client.disconnect()
        _client = None
