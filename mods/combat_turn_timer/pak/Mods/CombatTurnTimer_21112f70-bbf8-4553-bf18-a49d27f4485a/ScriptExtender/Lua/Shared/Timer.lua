local Timer = {
    MIN_SECONDS = 5,
    MAX_SECONDS = 300,
    DEFAULT_SECONDS = 60,
    State = Ext.Net.CreateChannel(ModuleUUID, "State"),
    SetLimit = Ext.Net.CreateChannel(ModuleUUID, "SetLimit"),
}

function Timer.ParseLimit(seconds)
    if type(seconds) ~= "number" or seconds ~= seconds then
        return nil
    end
    return math.floor(math.max(Timer.MIN_SECONDS, math.min(Timer.MAX_SECONDS, seconds)) + 0.5)
end

return Timer
