-- Welding visualization - draws red dots at tip position
-- Add to CoppeliaSim: Right-click Tip -> Add -> Associated Child Script

function sysCall_init()
    print("Welding visual script loaded")
end

function sysCall_sensing()
    local w = sim.getInt32Signal('welding')
    
    -- Draw welding point when welding is active
    if w == 1 then
        local tip = sim.getObjectHandle('Tip')
        if tip >= 0 then
            local pos = sim.getObjectPosition(tip, -1)
            -- Draw small red dot at tip position
            sim.addDrawingObject(0, 0, 0, -1, 4, {1, 0.2, 0}, {pos[1], pos[2], pos[3]}, nil, nil)
        end
    end
end
