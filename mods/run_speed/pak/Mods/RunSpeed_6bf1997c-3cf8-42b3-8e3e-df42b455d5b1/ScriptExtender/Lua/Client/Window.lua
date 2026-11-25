-- Small collapsible window at the right screen edge: slider and presets for the multiplier.
-- The server owns the value; the window only sends requests and shows what the server reports.

local Speed = Ext.Require("Shared/Speed.lua")
local Channels = Speed.Channels

local TEXT = {
    English = {
        Title = "Run speed",
        Hint = "Combat and turn-based mode: normal speed",
    },
    Russian = {
        Title = "Скорость бега",
        Hint = "В бою и пошаговом режиме скорость обычная",
    },
}
local PRESETS = { 1, 2, 3, 5, 10 }
local EDGE_MARGIN = 16
local TOP_SHARE = 0.3
local SLIDER_WIDTH = 240
local BACKGROUND_ALPHA = 0.6

local window, slider, valueText

local function Text()
    local switches = Ext.Utils.GetGlobalSwitches()
    return TEXT[switches and switches.Language] or TEXT.English
end

local function Format(multiplier)
    return string.format("%.1fx", multiplier)
end

local function Show(multiplier)
    slider.Value = { multiplier, 0, 0, 0 }
    valueText.Label = Format(multiplier)
end

local function Send(multiplier)
    Channels.SetMultiplier:SendToServer({ Multiplier = Speed.Clamp(multiplier) })
end

local function CreateWindow()
    local text = Text()
    -- "###" keeps the window id stable when the title language changes
    window = Ext.IMGUI.NewWindow(text.Title .. "###RunSpeedWindow")
    window.Closeable = false
    window.AlwaysAutoResize = true
    window.NoFocusOnAppearing = true
    window:SetBgAlpha(BACKGROUND_ALPHA)
    local viewport = Ext.IMGUI.GetViewportSize()
    window:SetPos({ viewport[1] - EDGE_MARGIN, viewport[2] * TOP_SHARE }, "FirstUseEver", { 1, 0 })

    valueText = window:AddText(Format(Speed.DEFAULT))
    slider = window:AddSlider("##RunSpeedMultiplier", Speed.DEFAULT, Speed.MIN, Speed.MAX)
    slider.Logarithmic = true
    slider.ItemWidth = SLIDER_WIDTH
    slider.OnChange = function(_, value)
        valueText.Label = Format(Speed.Clamp(value[1]))
    end
    -- Sent on release, not on every drag step
    slider.OnDeactivate = function()
        Send(slider.Value[1])
    end

    for index, preset in ipairs(PRESETS) do
        local button = window:AddButton(string.format("%dx", preset))
        button.SameLine = index > 1
        button.OnClick = function()
            Show(preset)
            Send(preset)
        end
    end
    window:AddText(text.Hint)
end

Channels.State:SetHandler(function(data)
    if window then
        Show(Speed.Clamp(data.Multiplier))
    end
end)

Channels.Template:SetHandler(function(data)
    for _, character in ipairs(data.Characters) do
        local entity = Ext.Entity.Get(character)
        local client = entity and entity.ClientCharacter
        local template = client and client.Template
        if template then
            Speed.Write(template, data.Values)
        end
    end
end)

Ext.Events.GameStateChanged:Subscribe(function(e)
    if e.ToState == "Running" then
        if window == nil then
            CreateWindow()
        end
        window.Open = true
        Channels.State:RequestToServer({}, function(data)
            Show(Speed.Clamp(data.Multiplier))
        end)
    elseif e.FromState == "Running" and window then
        window.Open = false
    end
end)
