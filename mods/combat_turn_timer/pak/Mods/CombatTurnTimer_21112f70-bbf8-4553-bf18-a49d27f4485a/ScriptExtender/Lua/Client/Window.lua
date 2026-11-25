local Timer = Ext.Require("Shared/Timer.lua")

local TEXT = {
    English = {
        Title = "Combat turn timer",
        Limit = "Turn limit (seconds)",
        Apply = "Apply",
        Waiting = "Waiting for your turn",
        Outside = "Outside combat",
        Active = "%d active turns",
    },
    Russian = {
        Title = "Таймер хода",
        Limit = "Время на ход (сек.)",
        Apply = "Применить",
        Waiting = "Ожидание вашего хода",
        Outside = "Вне боя",
        Active = "Активных ходов: %d",
    },
}

local text, window, countdown, progress, slider, activeText
local limit = Timer.DEFAULT_SECONDS
local inCombat = false

local function Format(remaining)
    local seconds = math.ceil(remaining / 1000)
    return string.format("%02d:%02d", seconds // 60, seconds % 60)
end

local function Color(fraction)
    -- Green to amber to red, with contrast against the dark window background.
    local red = math.min(1, 1.64 - 1.36 * fraction)
    local green = math.min(0.88, 0.24 + 1.40 * fraction)
    return { red, green, 0.27, 1 }
end

local function Show(state)
    if state.InCombat and not inCombat then
        window:SetCollapsed(false, "Always")
    end
    inCombat = state.InCombat
    if state.Seconds ~= limit then
        limit = state.Seconds
        slider.Value = { limit, 0, 0, 0 }
    end
    activeText.Visible = state.Active > 1
    if activeText.Visible then
        activeText.Label = string.format(text.Active, state.Active)
    end
    progress.Visible = state.Remaining ~= nil
    if progress.Visible then
        local fraction = state.Remaining / (state.Duration * 1000)
        countdown.Label = Format(state.Remaining)
        countdown:SetColor("Text", Color(fraction))
        progress.Value = fraction
        progress:SetColor("PlotHistogram", Color(fraction))
    else
        countdown.Label = inCombat and text.Waiting or text.Outside
        countdown:SetColor("Text", { 0.91, 0.91, 0.91, 1 })
    end
end

local function CreateWindow()
    local switches = Ext.Utils.GetGlobalSwitches()
    text = TEXT[switches and switches.Language] or TEXT.English
    window = Ext.IMGUI.NewWindow(text.Title .. "###CombatTurnTimerWindow")
    window.Closeable = false
    window.AlwaysAutoResize = true
    window.NoFocusOnAppearing = true
    window:SetBgAlpha(0.82)
    local viewport = Ext.IMGUI.GetViewportSize()
    window:SetPos({ viewport[1] * 0.18, viewport[2] * 0.15 }, "FirstUseEver", { 0, 0 })

    countdown = window:AddText(text.Outside)
    progress = window:AddProgressBar()
    progress.Size = { 216, 8 }
    progress.Overlay = " "
    progress.Visible = false
    activeText = window:AddText("")
    activeText.Visible = false
    window:AddSeparator()
    window:AddText(text.Limit)
    slider = window:AddSliderInt("##TurnLimit", limit, Timer.MIN_SECONDS, Timer.MAX_SECONDS)
    slider.ItemWidth = 144
    slider.AlwaysClamp = true
    local apply = window:AddButton(text.Apply)
    apply.SameLine = true
    apply.OnClick = function()
        Timer.SetLimit:SendToServer({ Seconds = slider.Value[1] })
    end
end

Timer.State:SetHandler(function(state)
    if window then
        Show(state)
    end
end)

Ext.Events.SessionLoading:Subscribe(function()
    inCombat = false
    limit = Timer.DEFAULT_SECONDS
    if window then
        slider.Value = { limit, 0, 0, 0 }
        Show({ Seconds = limit, InCombat = false, Active = 0 })
    end
end)

Ext.Events.GameStateChanged:Subscribe(function(event)
    if event.ToState == "Running" then
        if not window then
            CreateWindow()
        end
        window.Open = true
        Timer.State:SendToServer({})
    elseif event.FromState == "Running" and window then
        window.Open = false
    end
end)
