-- Script Lua pour mGBA : Charge le state 1 lorsque F1 est pressé

while true do
    local keys = emu.getKeyStatus()

    if keys["F1"] then
        savestate.load(1)
    end

    emu.frameadvance()
end