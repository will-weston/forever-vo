local _, ns = ...

--[[
Options panel built on the Settings API (Escape > Options > AddOns).
Boolean settings write straight into ns.db; dropdowns and the slider go through
proxy settings so the saved values stay readable strings/numbers.
]]

local SettingsPanel = {}
ns.SettingsPanel = SettingsPanel

local SOUND_CHANNELS = { "Master", "Dialog", "SFX", "Music", "Ambience" }

local function Checkbox(category, key, name, tooltip, onChange)
    local setting = Settings.RegisterAddOnSetting(category, "FVO_" .. key, key, ns.db, Settings.VarType.Boolean, name, ns.defaults[key])
    if onChange then
        setting:SetValueChangedCallback(function(_, value)
            onChange(value)
        end)
    end
    Settings.CreateCheckbox(category, setting, tooltip)
    return setting
end

local function Dropdown(category, key, name, tooltip, choices, onChange)
    -- choices: list of { value, label }, or a function returning one for choices
    -- that depend on the installed voice packs (they register after this panel
    -- is built). The stored value is choices[i][1]; the control sees the index.
    local function Choices()
        return type(choices) == "function" and choices() or choices
    end
    local function GetValue()
        for index, choice in ipairs(Choices()) do
            if choice[1] == ns.db[key] then
                return index
            end
        end
        return 1
    end
    local function SetValue(index)
        local choice = Choices()[index]
        if not choice then
            return
        end
        ns.db[key] = choice[1]
        if onChange then
            onChange(ns.db[key])
        end
    end
    local function GetOptions()
        local container = Settings.CreateControlTextContainer()
        for index, choice in ipairs(Choices()) do
            container:Add(index, choice[2])
        end
        return container:GetData()
    end
    local default = 1
    for index, choice in ipairs(Choices()) do
        if choice[1] == ns.defaults[key] then
            default = index
        end
    end
    local setting = Settings.RegisterProxySetting(category, "FVO_" .. key, Settings.VarType.Number, name, default, GetValue, SetValue)
    Settings.CreateDropdown(category, setting, GetOptions, tooltip)
    return setting
end

local function Slider(category, key, name, tooltip, minValue, maxValue, step, formatter, onChange)
    local function GetValue()
        return ns.db[key]
    end
    local function SetValue(value)
        ns.db[key] = value
        if onChange then
            onChange(value)
        end
    end
    local setting = Settings.RegisterProxySetting(category, "FVO_" .. key, Settings.VarType.Number, name, ns.defaults[key], GetValue, SetValue)
    local options = Settings.CreateSliderOptions(minValue, maxValue, step)
    options:SetLabelFormatter(MinimalSliderWithSteppersMixin.Label.Right, formatter)
    Settings.CreateSlider(category, setting, options, tooltip)
    return setting
end

function SettingsPanel:Open()
    if self.category then
        Settings.OpenToCategory(self.category:GetID())
    end
end

ns.OnInit(function()
    local category, layout = Settings.RegisterVerticalLayoutCategory("Forever Voiceover")
    SettingsPanel.category = category
    local head = ns.UI.TalkingHead

    local function RefreshHead()
        head:ApplySettings()
    end

    -- Everyday choices on the landing page.
    layout:AddInitializer(CreateSettingsListSectionHeaderInitializer("Playback"))
    Checkbox(category, "playAccept", "Quest offers", "Read the quest text when a quest is offered.")
    Checkbox(category, "playComplete", "Quest turn-ins", "Read the reward text when handing in a quest.")
    Checkbox(category, "playProgress", "Quest progress", "Read the reminder when you return before a quest is complete.")
    Checkbox(category, "stopOnClose", "Stop when closing quest dialogue", "Stop the current line when you close the quest or gossip window. Leave off to keep listening as you move on.")

    layout:AddInitializer(CreateSettingsListSectionHeaderInitializer("Appearance"))
    Checkbox(category, "showHead", "Show dialogue panel", "Show the speaker and quest while a line plays. The X skips the current line.", RefreshHead)
    Checkbox(category, "showText", "Show subtitles", "Display the spoken text in the dialogue panel.", RefreshHead)
    Slider(category, "headScale", "Panel size", "Resize the dialogue panel. Drag the panel to move it; position locking is in Advanced.", 0.5, 1.5, 0.05, function(value) return format("%d%%", value * 100) end, RefreshHead)
    Checkbox(category, "showMinimapButton", "Minimap button", "Left-click for settings. Right-click for playback controls. Drag to move.", function() ns.UI.MinimapButton:ApplySettings() end)

    local advanced, advancedLayout = Settings.RegisterVerticalLayoutSubcategory(category, "Advanced")
    advancedLayout:AddInitializer(CreateSettingsListSectionHeaderInitializer("Audio"))
    local channels = {}
    for _, channel in ipairs(SOUND_CHANNELS) do
        table.insert(channels, { channel, channel })
    end
    Dropdown(advanced, "soundChannel", "Volume channel", "Which of the game's volume sliders controls voiceovers.", channels)
    Checkbox(advanced, "muteGameDialog", "Mute overlapping NPC voices", "Temporarily mute the game's Dialog channel while a voiceover plays. Does not apply if voiceovers use the Dialog channel.")

    advancedLayout:AddInitializer(CreateSettingsListSectionHeaderInitializer("Position"))
    Checkbox(advanced, "lockHead", "Lock dialogue panel", "Prevent the dialogue panel from being dragged.")
    Checkbox(advanced, "lockMinimapButton", "Lock minimap button", "Prevent the minimap button from being dragged.")
    advancedLayout:AddInitializer(CreateSettingsButtonInitializer("Dialogue position", "Reset position", function()
        head.frame:ResetPosition()
    end, "Move the dialogue panel back to the bottom center of the screen.", true))

    advancedLayout:AddInitializer(CreateSettingsListSectionHeaderInitializer("Voice pack tools"))
    Checkbox(advanced, "capture", "Save dialogue for voice generation", "Save quest and conversation text you encounter so new voice lines can be generated.")
    Checkbox(advanced, "notifyUnvoiced", "Missing voice notices", "Print a chat message when dialogue has no audio yet.")
    Checkbox(advanced, "debug", "Debug messages", "Print matching details to chat.")

    Settings.RegisterAddOnCategory(category)
end)
