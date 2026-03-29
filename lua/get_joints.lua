# Copy and paste this into CoppeliaSim's script editor (Lua)

jointHandles={}
for i=1,6,1 do
    jointHandles[i]=sim.getObjectHandle('IRB4600_joint'..i)
end

tipHandle=sim.getObjectHandle('Tip')

print("=== JOINT ANGLES (radians) ===")
for i=1,6,1 do
    pos=sim.getJointPosition(jointHandles[i])
    print(string.format("Joint%d: %.6f", i, pos))
end

tipPos=sim.getObjectPosition(tipHandle,-1)
print(string.format("\n=== TIP POSITION ==="))
print(string.format("X: %.5f, Y: %.5f, Z: %.5f", tipPos[1], tipPos[2], tipPos[3]))
print(string.format("Z above cube: %.5f", tipPos[3]-1.075))
