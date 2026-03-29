-- Home Position Script for IRB4600 Robot
-- Usage: Load this script in CoppeliaSim, then type moveHome() in console

function sysCall_init()
    -- Get joint handles
    jointHandles = {}
    for i = 1, 6, 1 do
        jointHandles[i] = sim.getObjectHandle('IRB4600_joint' .. i)
    end
    
    -- Home position (radians) - torch ON cube surface
    homePos = {-0.038863, 0.160718, 0.359108, 0.000310, -0.074666, 0.0}
    
    print("=== Home Position Script Loaded ===")
    print("Type 'moveHome()' in console to move to home position")
end

function moveHome()
    -- Move each joint to home position using target position
    for i = 1, 6, 1 do
        sim.setJointTargetPosition(jointHandles[i], homePos[i])
    end
    print("Moving to home position...")
end

function moveHomeDirect()
    -- Direct position setting (for kinematic mode)
    for i = 1, 6, 1 do
        sim.setJointPosition(jointHandles[i], homePos[i])
    end
    print("Moving to home position (direct)...")
end

function getJointPositions()
    -- Print current joint positions
    print("=== Current Joint Positions ===")
    for i = 1, 6, 1 do
        local pos = sim.getJointPosition(jointHandles[i])
        print(string.format("Joint%d: %.6f rad (%.2f deg)", i, pos, pos * 180 / math.pi))
    end
end
