local _, ns = ...
local Util, Queue = ns.Util, ns.Queue

-- A compact quest dialog: native circular portrait and name bar above
-- parchment, with spoken text paged in time with the audio.
-- Right-click or the X skips the current line.

local FRAME_WIDTH, FRAME_HEIGHT = 500, 239
local FOOTER_HEIGHT = 34
local PAGE_CHARS = 330

local TalkingHead = {
    displayed = nil,
    pageTimers = {},
    portraits = {},
}
ns.UI.TalkingHead = TalkingHead

local function Alpha(group, target, fromAlpha, toAlpha, duration)
    local anim = group:CreateAnimation("Alpha")
    anim:SetTarget(target)
    anim:SetFromAlpha(fromAlpha)
    anim:SetToAlpha(toAlpha)
    anim:SetDuration(duration)
    anim:SetOrder(1)
end

function TalkingHead.EventIcon(item)
    local event = item.event
    if event == "accept" then
        return ns.mediaPath .. "BulletAccept"
    elseif event == "progress" then
        return ns.mediaPath .. "BulletProgress"
    elseif event == "complete" then
        return ns.mediaPath .. "BulletComplete"
    end
    return ns.mediaPath .. "BulletGossip"
end

-- ---------------------------------------------------------------------------
-- Construction
-- ---------------------------------------------------------------------------

function TalkingHead:Init()
    self:CreateFrame()
    self:CreatePortrait()
    self:CreateText()
    self:CreateControls()
    self:CreateAnimations()
    self:ApplyTextureKit()
    self:ApplySettings()

    Queue:RegisterCallback("OnChanged", self.Update, self)
    Queue:RegisterCallback("OnPause", self.UpdatePause, self)
    Queue:RegisterCallback("OnPlay", function(_, item)
        if self.displayed == item then
            self:ShowPagedText(item)
        end
    end, self)
end

function TalkingHead:CreateFrame()
    local frame = CreateFrame("Button", "ForeverVOTalkingHead", UIParent, "PortraitFrameTemplate")
    self.frame = frame
    frame:SetSize(FRAME_WIDTH, FRAME_HEIGHT)
    frame:SetFrameStrata("HIGH")
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:RegisterForClicks("RightButtonUp")
    frame:RegisterForDrag("LeftButton")
    frame:Hide()

    function frame:ResetPosition()
        self:ClearAllPoints()
        self:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 96)
    end
    frame:ResetPosition()
    frame:SetUserPlaced(true)

    frame:SetScript("OnClick", function(_, button)
        if button == "RightButton" then
            Queue:Skip()
        end
    end)
    frame:SetScript("OnDragStart", function(self)
        if not ns.db.lockHead then
            self:StartMoving()
        end
    end)
    frame:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
    end)

    -- The same title bar, round portrait border, and rock surround as QuestFrame.
    frame.TextBackground = frame:CreateTexture(nil, "BACKGROUND", nil, -1)
    frame.TextBackground:SetPoint("TOPLEFT", 7, -62)
    frame.TextBackground:SetPoint("BOTTOMRIGHT", -7, 9 + FOOTER_HEIGHT)

    frame.CloseButton:SetScript("OnClick", function()
        PlaySound(SOUNDKIT.IG_MAINMENU_CLOSE)
        Queue:Skip()
    end)
    frame.CloseButton:SetScript("OnEnter", function(button)
        GameTooltip:SetOwner(button, "ANCHOR_TOP")
        GameTooltip:SetText("Close")
        GameTooltip:Show()
    end)
    frame.CloseButton:SetScript("OnLeave", GameTooltip_Hide)
end

function TalkingHead:CreatePortrait()
    local frame = self.frame
    frame.Portrait = frame.PortraitContainer.portrait
    frame.Portrait:SetTexture(ns.mediaPath .. "Book")
end

function TalkingHead:CachePortraits()
    -- Snapshot queued speakers while their unit is available. A texture retains
    -- its portrait after the dialog closes or the player targets someone else.
    for _, unit in ipairs({ "questnpc", "npc", "target" }) do
        local key = UnitExists(unit) and Util.SpeakerKeyFromGUID(UnitGUID(unit))
        if key and Util.IsCreatureKey(key) and not self.portraits[key] then
            for i = 1, Queue:Size() do
                if Queue:Get(i).speakerKey == key then
                    local portrait = self.frame.PortraitContainer:CreateTexture(nil, "OVERLAY")
                    portrait:SetAllPoints(self.frame.Portrait)
                    portrait:AddMaskTexture(self.frame.PortraitContainer.CircleMask)
                    portrait:Hide()
                    SetPortraitTexture(portrait, unit)
                    self.portraits[key] = portrait
                    break
                end
            end
        end
    end
end

function TalkingHead:CreateText()
    local frame = self.frame

    frame.Name = frame.TitleContainer.TitleText
    frame:SetTitleOffsets(64, -32)
    frame.Name:SetFontObject("GameFontNormal")
    frame.Name:SetJustifyH("CENTER")

    frame.Title = frame:CreateFontString(nil, "ARTWORK")
    frame.Title:SetFontObject("QuestTitleFont")
    frame.Title:SetJustifyH("LEFT")
    frame.Title:SetPoint("TOPLEFT", 19, -72)
    frame.Title:SetPoint("RIGHT", -19, 0)
    frame.Title:SetWordWrap(false)

    frame.Text = frame:CreateFontString(nil, "ARTWORK")
    frame.Text:SetFontObject("QuestFont")
    frame.Text:SetJustifyH("LEFT")
    frame.Text:SetJustifyV("TOP")
    frame.Text:SetPoint("TOPLEFT", frame.Title, "BOTTOMLEFT", 0, -6)
    frame.Text:SetPoint("BOTTOMRIGHT", -19, 19 + FOOTER_HEIGHT)
    frame.Text:SetWordWrap(true)
    if AutoScalingFontStringMixin then
        Mixin(frame.Text, AutoScalingFontStringMixin)
        frame.Text.minLineHeight = 12
    end
end

function TalkingHead:CreateControls()
    local frame = self.frame

    -- Keep playback together in the quest-style footer; the title bar is for
    -- the speaker and close button.
    local skip = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    frame.SkipButton = skip
    skip:SetSize(86, 24)
    skip:SetPoint("BOTTOMRIGHT", -14, 12)
    skip:SetText("Skip")
    skip:SetScript("OnClick", function()
        if Queue:Current() then
            PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
            Queue:Skip()
        end
    end)
    skip:SetScript("OnEnter", function(button)
        GameTooltip:SetOwner(button, "ANCHOR_TOP")
        GameTooltip:SetText("Skip")
        GameTooltip:Show()
    end)
    skip:SetScript("OnLeave", GameTooltip_Hide)
    skip:SetScript("OnHide", function()
        if GameTooltip:GetOwner() == skip then GameTooltip:Hide() end
    end)

    local button = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    frame.PauseButton = button
    button:SetSize(86, 24)
    button:SetPoint("RIGHT", skip, "LEFT", -8, 0)
    button:SetText("Pause")
    button:SetScript("OnClick", function()
        PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
        Queue:TogglePause()
    end)
    button:SetScript("OnEnter", function()
        self:ShowPauseTooltip()
    end)
    button:SetScript("OnLeave", GameTooltip_Hide)
    button:SetScript("OnHide", function()
        if GameTooltip:GetOwner() == button then GameTooltip:Hide() end
    end)
end

function TalkingHead:ShowPauseTooltip()
    local button = self.frame.PauseButton
    GameTooltip:SetOwner(button, "ANCHOR_TOP")
    GameTooltip:SetText(Queue:IsPaused() and "Play from beginning" or "Pause")
    GameTooltip:Show()
end

function TalkingHead:CreateAnimations()
    local frame = self.frame
    local fadeIn = frame:CreateAnimationGroup()
    fadeIn:SetToFinalAlpha(true)
    Alpha(fadeIn, frame, 0, 1, 0.15)
    frame.FadeIn = fadeIn

    local close = frame:CreateAnimationGroup()
    close:SetToFinalAlpha(true)
    Alpha(close, frame, 1, 0, 0.2)
    close:SetScript("OnFinished", function()
        frame:Hide()
        frame:SetAlpha(1)
        frame.isClosing = nil
    end)
    frame.Close = close
end

-- ---------------------------------------------------------------------------
-- Styling and settings
-- ---------------------------------------------------------------------------

function TalkingHead:ApplyTextureKit()
    local frame = self.frame
    local parchment = ns.db.factionHead ~= false
    if parchment then
        frame.TextBackground:SetAtlas("QuestBG-Parchment")
        frame.Title:SetTextColor(0.18, 0.12, 0.06)
        frame.Text:SetTextColor(0.12, 0.08, 0.04)
    else
        frame.TextBackground:SetColorTexture(0.08, 0.07, 0.06, 1)
        frame.Title:SetTextColor(1, 0.82, 0.02)
        frame.Text:SetTextColor(0.95, 0.92, 0.85)
    end
    frame.Name:SetTextColor(1, 0.82, 0.02)
    frame.Title:SetShadowColor(0, 0, 0, parchment and 0 or 1)
    frame.Text:SetShadowColor(0, 0, 0, parchment and 0 or 1)
end

function TalkingHead:ApplySettings()
    local frame = self.frame
    frame:SetScale(ns.db.headScale or 1)
    self:ApplyTextureKit()
    frame.Text:SetShown(ns.db.showText ~= false)
    if not ns.db.showHead then
        self:CloseFrame()
    end
    self:Update()
end

-- ---------------------------------------------------------------------------
-- Display
-- ---------------------------------------------------------------------------

function TalkingHead:CancelPageTimers()
    for _, timer in ipairs(self.pageTimers) do
        timer:Cancel()
    end
    wipe(self.pageTimers)
end

function TalkingHead:ShowPagedText(item)
    self:CancelPageTimers()
    local frame = self.frame
    local pages = Util.Paginate(item.text, PAGE_CHARS)
    frame.Text:SetText(pages[1])
    if #pages == 1 or not item.duration or Queue:IsPaused() then
        return
    end
    local total = 0
    for _, page in ipairs(pages) do
        total = total + #page
    end
    local elapsed = #pages[1]
    for i = 2, #pages do
        local at = item.duration * (elapsed / total)
        local page = pages[i]
        table.insert(self.pageTimers, C_Timer.NewTimer(at, function()
            if self.displayed == item then
                frame.Text:SetText(page)
            end
        end))
        elapsed = elapsed + #page
    end
end

function TalkingHead:SetPortrait(item)
    if self.activePortrait then self.activePortrait:Hide() end
    local portrait = item.speakerKey and self.portraits[item.speakerKey]
    self.activePortrait = portrait
    self.frame.Portrait:SetShown(not portrait)
    if portrait then portrait:Show() end
end

function TalkingHead:Present(item)
    local frame = self.frame
    local wasShown = frame:IsShown() and not frame.isClosing

    frame.Close:Stop()
    frame.isClosing = nil
    frame:SetAlpha(1)
    self.displayed = item
    self:SetPortrait(item)
    frame.Name:SetText(item.name or "")
    frame.Title:SetText(item.title or "")
    self:ShowPagedText(item)
    frame:Show()
    if not wasShown then frame.FadeIn:Play() end
end

function TalkingHead:CloseFrame()
    local frame = self.frame
    self.displayed = nil
    self:CancelPageTimers()
    if frame:IsShown() and not frame.isClosing then
        frame.isClosing = true
        frame.FadeIn:Stop()
        frame.Close:Play()
    end
end

function TalkingHead:Update()
    self:CachePortraits()
    local frame = self.frame
    local current = Queue:Current()

    if not current or not ns.db.showHead then
        self:CloseFrame()
    elseif current ~= self.displayed then
        self:Present(current)
    else
        self:SetPortrait(current)
    end

    frame.CloseButton:SetEnabled(current ~= nil)
    frame.PauseButton:SetEnabled(current ~= nil)
    frame.SkipButton:SetEnabled(current ~= nil)
    self:UpdatePause(Queue:IsPaused())
end

function TalkingHead:UpdatePause(paused)
    local frame = self.frame
    frame.PauseButton:SetText(paused and "Play" or "Pause")
    if frame.PauseButton:IsMouseOver() and GameTooltip:GetOwner() == frame.PauseButton then
        self:ShowPauseTooltip()
    end
    if paused then
        self:CancelPageTimers()
    end
end

ns.OnInit(function()
    TalkingHead:Init()
end)
