-- Simple weld control script in Coppelia
-- Add this script to your scene: Add → Script → Customization

function getAllObjectNames(inInts, inFloats, inStrings, inBuffer)
    local allObjects = sim.getObjectsInTree(sim.handle_scene)
    local names = ""
    for i = 1, #allObjects do
        local name = sim.getObjectName(allObjects[i])
        if names == "" then
            names = name
        else
            names = names .. "\0" .. name
        end
    end
    return {}, {}, names, ''
end

function clearWeldObjects(inInts, inFloats, inStrings, inBuffer)
    local cleared = 0
    local allObjects = sim.getObjectsInTree(sim.handle_scene)
    local keywords = {'weld', 'trace', 'wire', 'mark', 'line', 'bead'}
    
    for i = 1, #allObjects do
        local name = sim.getObjectName(allObjects[i])
        local nameLower = string.lower(name)
        for _, kw in ipairs(keywords) do
            if string.find(nameLower, kw) then
                sim.removeObject(allObjects[i])
                cleared = cleared + 1
                break
            end
        end
    end
    
    return {cleared}, {}, {}, ''
end

-- Signal-based clearing (works every time signal is received)
function sysCall_sensing()
    local clearVal = sim.getInt32Signal('clear_weld')
    if clearVal and clearVal == 1 then
        local cleared = 0
        local allObjects = sim.getObjectsInTree(sim.handle_scene)
        local keywords = {'weld', 'trace', 'wire', 'mark', 'line', 'bead'}
        
        for i = 1, #allObjects do
            local name = sim.getObjectName(allObjects[i])
            local nameLower = string.lower(name)
            for _, kw in ipairs(keywords) do
                if string.find(nameLower, kw) then
                    sim.removeObject(allObjects[i])
                    cleared = cleared + 1
                    break
                end
            end
        end
        
        sim.clearInt32Signal('clear_weld')
        print("Cleared " .. cleared .. " weld mark object(s)")
    end
end
