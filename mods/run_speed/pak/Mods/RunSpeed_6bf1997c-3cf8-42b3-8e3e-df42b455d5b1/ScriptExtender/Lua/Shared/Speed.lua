-- Multiplier limits, template fields and net channels shared by server and client.

local Speed = {
    MIN = 0.5,
    MAX = 10.0,
    DEFAULT = 1.0,
    -- CharacterTemplate fields for walking and running speed and how fast it is reached
    FIELDS = {
        "MovementSpeedStroll",
        "MovementSpeedWalk",
        "MovementSpeedRun",
        "MovementSpeedSprint",
        "MovementSpeedDash",
        "MovementAcceleration",
    },
}

Speed.Channels = {
    SetMultiplier = Ext.Net.CreateChannel(ModuleUUID, "SetMultiplier"),
    State = Ext.Net.CreateChannel(ModuleUUID, "State"),
    Template = Ext.Net.CreateChannel(ModuleUUID, "Template"),
}

--- Limits to [MIN, MAX] and rounds to 0.1; anything that is not a number gives DEFAULT.
function Speed.Clamp(value)
    local number = tonumber(value)
    if number == nil or number ~= number then
        return Speed.DEFAULT
    end
    number = math.max(Speed.MIN, math.min(Speed.MAX, number))
    return math.floor(number * 10 + 0.5) / 10
end

function Speed.Capture(template)
    local values = {}
    for _, field in ipairs(Speed.FIELDS) do
        values[field] = template[field]
    end
    return values
end

function Speed.Scale(originals, multiplier)
    local values = {}
    for field, value in pairs(originals) do
        values[field] = value * multiplier
    end
    return values
end

function Speed.Write(template, values)
    for field, value in pairs(values) do
        template[field] = value
    end
end

return Speed
