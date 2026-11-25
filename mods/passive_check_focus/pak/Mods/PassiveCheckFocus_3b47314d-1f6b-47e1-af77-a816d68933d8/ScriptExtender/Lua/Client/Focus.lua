local Channels = Ext.Require("Shared/Channel.lua")

local focusRequest

local function Controller(guid)
    local entity = Ext.Entity.Get(guid)
    local character = entity and entity.ClientCharacter
    return character and character.InputController
end

Channels.Stop:SetRequestHandler(function(data)
    if Ext.Utils.GetGameState() ~= "Running" then
        return { Ready = false }
    end
    for character in pairs(data.Characters) do
        local controller = Controller(character)
        local task = controller and controller.RunningTask
        if task and task.TaskType == "MoveTo" then
            controller.RequestFlags = controller.RequestFlags | "RequestCancelMovement"
        end
    end
    return { Ready = true }
end)

local function CameraContext()
    local root = Ext.UI.GetRoot()
    local content = root and root:Find("ContentRoot")
    if not content then
        return nil
    end
    for index = 1, content.ChildrenCount do
        local widget = content:Child(index)
        if widget and (widget.Name == "PlayerPortraits" or widget.Name == "HotBar") then
            return widget.DataContext
        end
    end
end

Channels.Focus:SetHandler(function(data)
    focusRequest = { Character = data.Character, Deadline = Ext.Timer.MonotonicTime() + 750 }
end)

Ext.Events.GameStateChanged:Subscribe(function(event)
    if event.FromState == "Running" then
        focusRequest = nil
    end
end)

Ext.Events.Tick:Subscribe(function()
    local request = focusRequest
    if not request then
        return
    end
    if Ext.Timer.MonotonicTime() >= request.Deadline then
        focusRequest = nil
        return
    end

    -- The server's selection change must reach this client before the portrait command.
    local controller = Controller(request.Character)
    if not controller or not controller.Active or request.Queued then
        return
    end
    request.Queued = true
    Ext.UI.Defer(function()
        if focusRequest ~= request then
            return
        end
        request.Queued = false
        local context = CameraContext()
        local player = context and context.CurrentPlayer
        local selected = player and player.SelectedCharacter
        local camera = context and context.SetCameraOnGameObject
        if selected and camera and camera:CanExecute(selected) then
            focusRequest = nil
            camera:Execute(selected)
        end
    end)
end)
