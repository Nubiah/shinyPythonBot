local socket = require("socket")
local client = socket.connect("localhost", 5000)

function isShiny(pid, tid, sid)
  local xor1 = bit32.bxor(tid, sid)
  local xor2 = bit32.bxor(bit32.rshift(pid, 16), bit32.band(pid, 0xFFFF))
  local result = bit32.bxor(xor1, xor2)
  return result < 8
end

emu.addEventCallback(emu.callbackType.endFrame, function()
  local pid = memory.read32(0x02024284)
  local tid = memory.read16(0x02000000)
  local sid = memory.read16(0x02000002)

  if isShiny(pid, tid, sid) then
    client:send("shiny\n")
  end
end)
