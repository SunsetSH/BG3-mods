-- Scales the movement fields of party members' character templates out of combat.
-- Templates outlive a loaded save inside one game process, so every change is undone
-- whenever the server leaves the Running state (save, pause, level or session unload).

local Speed = Ext.Require("Shared/Speed.lua")
local Channels = Speed.Channels

-- Restored from the savegame before SessionLoaded: { Multiplier = number }
PersistentVars = {}

-- Template id -> field values before this mod changed them
local originals = {}
-- Template id -> { Multiplier = applied value, Characters = guids that use the template }
local applied = {}

local function Multiplier()
    return Speed.Clamp(PersistentVars.Multiplier or Speed.DEFAULT)
end

-- Osiris passes "Name_<uuid>", entity and template lookups need the bare uuid
local function Guid(object)
    return string.sub(object, -36)
end

local function IsTurnBased(character)
    return Osi.IsInCombat(character) == 1 or Osi.IsInForceTurnBasedMode(character) == 1
end

local function CharacterTemplate(character)
    local entity = Ext.Entity.Get(character)
    local server = entity and entity.ServerCharacter
    return server and server.Template
end

-- Template id -> { Characters, TurnBased } over all party members. Members can share a
-- template, then one member in combat keeps the template at normal speed for all of them.
local function PartyTemplates()
    local templates = {}
    for _, row in pairs(Osi.DB_PartyMembers:Get(nil)) do
        local character = Guid(row[1])
        local template = CharacterTemplate(character)
        if template then
            local entry = templates[template.Id] or { Characters = {}, TurnBased = false }
            table.insert(entry.Characters, character)
            entry.TurnBased = entry.TurnBased or IsTurnBased(character)
            templates[template.Id] = entry
        end
    end
    return templates
end

local function FindTemplate(id, characters)
    for _, character in ipairs(characters) do
        local template = CharacterTemplate(character)
        if template and template.Id == id then
            return template
        end
    end
    return Ext.Template.GetTemplate(id)
end

-- Clients keep their own template copies, so they get the same absolute values
local function Apply(id, characters, multiplier)
    local template = FindTemplate(id, characters)
    if template == nil then
        return
    end
    originals[id] = originals[id] or Speed.Capture(template)
    local values = Speed.Scale(originals[id], multiplier)
    Speed.Write(template, values)
    Channels.Template:Broadcast({ Characters = characters, Values = values })
end

local function Refresh()
    local multiplier = Multiplier()
    local party = PartyTemplates()
    for id, entry in pairs(party) do
        local target = entry.TurnBased and Speed.DEFAULT or multiplier
        local previous = applied[id]
        if previous == nil or previous.Multiplier ~= target then
            Apply(id, entry.Characters, target)
        end
        applied[id] = { Multiplier = target, Characters = entry.Characters }
    end
    for id, entry in pairs(applied) do
        if party[id] == nil then
            Apply(id, entry.Characters, Speed.DEFAULT)
            applied[id] = nil
        end
    end
end

local function RestoreAll()
    for id, entry in pairs(applied) do
        Apply(id, entry.Characters, Speed.DEFAULT)
    end
    applied = {}
end

local function BroadcastState()
    Channels.State:Broadcast({ Multiplier = Multiplier() })
end

Channels.SetMultiplier:SetHandler(function(data)
    PersistentVars.Multiplier = Speed.Clamp(data.Multiplier)
    Refresh()
    BroadcastState()
end)

-- A client that has just connected has none of the template values yet
Channels.State:SetRequestHandler(function()
    for id, entry in pairs(applied) do
        Apply(id, entry.Characters, entry.Multiplier)
    end
    return { Multiplier = Multiplier() }
end)

local function RefreshForPartyMember(object)
    if Osi.IsPartyMember(object, 0) == 1 then
        Refresh()
    end
end

Ext.Osiris.RegisterListener("EnteredCombat", 2, "after", RefreshForPartyMember)
Ext.Osiris.RegisterListener("LeftCombat", 2, "after", RefreshForPartyMember)
Ext.Osiris.RegisterListener("EnteredForceTurnBased", 1, "after", RefreshForPartyMember)
Ext.Osiris.RegisterListener("LeftForceTurnBased", 1, "after", RefreshForPartyMember)
Ext.Osiris.RegisterListener("CharacterJoinedParty", 1, "after", function()
    Refresh()
end)
Ext.Osiris.RegisterListener("CharacterLeftParty", 1, "after", function()
    Refresh()
end)
Ext.Osiris.RegisterListener("LevelGameplayStarted", 2, "after", function()
    Refresh()
    BroadcastState()
end)

Ext.Events.GameStateChanged:Subscribe(function(e)
    if e.ToState == "Running" then
        Refresh()
    elseif e.FromState == "Running" then
        RestoreAll()
    end
end)
