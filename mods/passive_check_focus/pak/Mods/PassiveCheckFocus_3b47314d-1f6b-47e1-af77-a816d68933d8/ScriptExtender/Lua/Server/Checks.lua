local Channels = Ext.Require("Shared/Channel.lua")

local UNASSIGNED_USER = -65536
local pending = {}

-- Several linked party members can roll at the same point. Stop all their
-- movement orders and use the first roller as the camera target for this user.
local function Flush()
    local batches = pending
    pending = {}
    if Ext.Utils.GetGameState() ~= "Running" then
        return
    end
    for user, batch in pairs(batches) do
        local roller = batch.Roller
        if Osi.GetReservedUserID(roller) == user then
            Channels.Stop:RequestToClient({ Characters = batch.Characters }, user, function(result)
                if not result.Ready or Ext.Utils.GetGameState() ~= "Running"
                    or Osi.GetReservedUserID(roller) ~= user then
                    return
                end
                if string.sub(Osi.GetCurrentCharacter(user) or "", -36) ~= roller then
                    Osi.MakePlayerActive(roller)
                end
                Channels.Focus:SendToClient({ Character = roller }, user)
            end)
        end
    end
end

Ext.Osiris.RegisterListener("RollResult", 6, "after", function(_, roller, _, result, isActive)
    if isActive ~= 0 or (result ~= 0 and result ~= 1) or Osi.IsPlayer(roller) ~= 1 then
        return
    end
    local user = Osi.GetReservedUserID(roller)
    if user == nil or user == UNASSIGNED_USER then
        return
    end

    if next(pending) == nil then
        Ext.OnNextTick(Flush)
    end
    local character = string.sub(roller, -36)
    local batch = pending[user]
    if not batch then
        batch = { Roller = character, Characters = {} }
        pending[user] = batch
    end
    batch.Characters[character] = true

    local controlled = Osi.GetCurrentCharacter(user)
    if controlled and Osi.InSamePartyGroup(roller, controlled) == 1 then
        batch.Characters[string.sub(controlled, -36)] = true
    end
end)
