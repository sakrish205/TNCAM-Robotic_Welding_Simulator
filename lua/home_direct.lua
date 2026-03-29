-- Home Position Script
-- Instructions:
-- 1. In CoppeliaSim, go to Menu -> Tools -> Script Editor
-- 2. File -> New
-- 3. Copy and paste this entire code
-- 4. Save as home.lua (optional)
-- 5. Press F5 to run THIS SCRIPT (not call from console)

-- Get joint handles
jointHandles = {}
for i = 1, 6, 1 do
    jointHandles[i] = sim.getObjectHandle('IRB4600_joint' .. i)
end

-- Home position (radians)
homePos = {-0.038863, 0.160718, 0.359108, 0.000310, -0.074666, 0.0}

print("Moving robot to home position...")

-- Move each joint
for i = 1, 6, 1 do
    sim.setJointTargetPosition(jointHandles[i], homePos[i])
end

print("Done! Robot should be moving to home position.")
