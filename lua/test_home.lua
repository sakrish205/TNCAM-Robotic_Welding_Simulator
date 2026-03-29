-- Test robot movement in CoppeliaSim

jointHandles={}
for i=1,6,1 do
    jointHandles[i]=sim.getObjectHandle('IRB4600_joint'..i)
end

tipHandle=sim.getObjectHandle('Tip')

-- Home position from calibration
homePos={-0.045721, -0.032085, 0.101161, -0.000124, -0.092324, 0.0}

print("=== SETTING HOME POSITION ===")
for i=1,6,1 do
    sim.setJointTargetPosition(jointHandles[i], homePos[i])
    print(string.format("Joint%d set to: %.6f", i, homePos[i]))
end

-- Wait for movement
sim.wait(2)

-- Check result
print("\n=== TIP POSITION ===")
tipPos=sim.getObjectPosition(tipHandle,-1)
print(string.format("Tip: X=%.5f, Y=%.5f, Z=%.5f", tipPos[1], tipPos[2], tipPos[3]))
print(string.format("Z above cube (1.075): %.5f", tipPos[3]-1.075))

print("\n=== JOINT POSITIONS ===")
for i=1,6,1 do
    pos=sim.getJointPosition(jointHandles[i])
    print(string.format("Joint%d: %.6f", i, pos))
end
