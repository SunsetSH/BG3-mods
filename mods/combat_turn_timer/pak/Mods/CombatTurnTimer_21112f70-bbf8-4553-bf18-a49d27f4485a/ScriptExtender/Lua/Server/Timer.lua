local Timer = Ext.Require("Shared/Timer.lua")

PersistentVars = {}

local SAMPLE_MS = 100
local END_RETRY_MS = 1000
local UNASSIGNED_USER = -65536
local turns, sent = {}, {}
local elapsed, previous, nextSample = 0, nil, 0
local running = Ext.Utils.GetGameState() == "Running"

local function Limit(profile)
    local limits = PersistentVars.Limits or {}
    return Timer.ParseLimit(limits[profile]) or Timer.DEFAULT_SECONDS
end

local function UserProfile(user)
    if user ~= nil and user ~= UNASSIGNED_USER then
        return Osi.GetUserProfileID(user)
    end
end

Timer.SetLimit:SetHandler(function(data, user)
    if not running or type(data) ~= "table" then
        return
    end
    local profile = UserProfile(user)
    local limit = Timer.ParseLimit(data.Seconds)
    if profile and limit then
        PersistentVars.Limits = PersistentVars.Limits or {}
        PersistentVars.Limits[profile] = limit
    end
end)

Timer.State:SetHandler(function(_, user)
    if user ~= nil then
        sent[user] = nil
    end
end)

local function TrackTurn(character, profile, view)
    if Osi.IsInCombat(character) ~= 1 then
        return
    end
    view.InCombat = true

    local entity = Ext.Entity.Get(character)
    local combat = entity and entity.TurnBased
    if not combat or not combat.IsActiveCombatTurn then
        return
    end

    local turn = turns[character]
    if not turn or turn.Combat ~= combat.Combat or turn.Profile ~= profile then
        turn = {
            Combat = combat.Combat,
            Profile = profile,
            Limit = view.Seconds,
            Deadline = elapsed + view.Seconds * 1000,
        }
    end
    turns[character] = turn
    turn.Seen = true
    if combat.RequestedEndTurn then
        return
    end

    local remaining = math.max(0, turn.Deadline - elapsed)
    if remaining == 0 and combat.CanActInCombat and elapsed >= (turn.RetryAt or 0) then
        turn.RetryAt = elapsed + END_RETRY_MS
        Osi.EndTurn(character)
    end
    view.Active = view.Active + 1
    if view.Remaining == nil or remaining < view.Remaining then
        view.Remaining = remaining
        view.Duration = turn.Limit
    end
end

local function Refresh()
    for _, turn in pairs(turns) do
        turn.Seen = false
    end

    local views = {}
    for _, row in pairs(Osi.DB_PartyMembers:Get(nil)) do
        local character = string.sub(row[1], -36)
        local user = Osi.GetReservedUserID(character)
        if user ~= nil and user ~= UNASSIGNED_USER and Osi.IsPlayer(character) == 1 then
            local view = views[user]
            if view == nil then
                local profile = UserProfile(user)
                if profile then
                    view = { Profile = profile, Seconds = Limit(profile), Active = 0, InCombat = false }
                    views[user] = view
                end
            end
            if view then
                TrackTurn(character, view.Profile, view)
            end
        end
    end

    for character, turn in pairs(turns) do
        if not turn.Seen then
            turns[character] = nil
        end
    end
    for user, view in pairs(views) do
        local last = sent[user]
        if not last or view.Profile ~= last.Profile or view.Seconds ~= last.Seconds
            or view.InCombat ~= last.InCombat or view.Remaining ~= last.Remaining
            or view.Duration ~= last.Duration or view.Active ~= last.Active then
            Timer.State:SendToClient({
                Seconds = view.Seconds,
                InCombat = view.InCombat,
                Remaining = view.Remaining,
                Duration = view.Duration,
                Active = view.Active,
            }, user)
        end
    end
    sent = views
end

Ext.Osiris.RegisterListener("TurnStarted", 1, "after", function(object)
    turns[string.sub(object, -36)] = nil
end)

Ext.Events.SessionLoading:Subscribe(function()
    turns, sent = {}, {}
    elapsed, previous, nextSample = 0, nil, 0
    running = false
end)

Ext.Events.GameStateChanged:Subscribe(function(event)
    running = event.ToState == "Running"
    previous, nextSample = nil, elapsed
    sent = {}
end)

Ext.Events.Tick:Subscribe(function()
    if not running then
        return
    end
    local now = Ext.Timer.MonotonicTime()
    if previous then
        elapsed = elapsed + now - previous
    end
    previous = now
    if elapsed >= nextSample then
        nextSample = elapsed + SAMPLE_MS
        Refresh()
    end
end)
