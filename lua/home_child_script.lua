--[[
    Home Position Script for IRB4600
    Instructions:
    1. In CoppeliaSim scene hierarchy, right-click on the robot base
    2. Add -> Associated Child Script -> Non-threaded
    3. Double-click the new script to open editor
    4. Replace contents with this code
    5. Run simulation (Press Play)
]]

function sysCall_init()
    -- Get joint handles
    jointHandles = {}
    for i = 1, 6, 1 do
        jointHandles[i] = sim.getObjectHandle('IRB4600_joint' .. i)
    end
    
    -- Home position (radians)
    homePos = {-0.038863, 0.160718, 0.359108, 0.000310, -0.074666, 0.0}
    
    print("=== Home Position Script Loaded ===")
    print("Robot will move to home position...")
    
    -- Move to home position on init
    for i = 1, 6, 1 do
        sim.setJointTargetPosition(jointHandles[i], homePos[i])
    end
end

function sysCall_actuation()
    -- This runs every simulation step
    -- Can add continuous control here if needed
end
