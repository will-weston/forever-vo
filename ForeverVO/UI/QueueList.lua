local _, ns = ...
local Queue = ns.Queue

-- Opened from settings, the minimap menu or /fvo queue. This window is
-- independent of the talking head, including when playback is idle or hidden.
local ROW_HEIGHT = 30
local MAX_VISIBLE_ROWS = 8
local PANEL_WIDTH = 420

local QueueList = {}
ns.UI.QueueList = QueueList

function QueueList:GetFrame()
    if self.frame then return self.frame end
    local frame = CreateFrame("Frame", "ForeverVOQueueList", UIParent, "TooltipBackdropTemplate")
    self.frame = frame
    frame:SetWidth(PANEL_WIDTH)
    frame:SetPoint("CENTER")
    frame:SetFrameStrata("DIALOG")
    frame:SetFrameLevel(100)
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetScript("OnDragStart", frame.StartMoving)
    frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
    frame:Hide()
    frame:SetScript("OnHide", function()
        ns.db.showQueuePanel = false
    end)
    table.insert(UISpecialFrames, "ForeverVOQueueList")

    frame.Header = frame:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    frame.Header:SetPoint("TOPLEFT", 16, -16)
    frame.Header:SetText("Playback queue")

    frame.CloseButton = CreateFrame("Button", nil, frame, "UIPanelCloseButtonNoScripts")
    frame.CloseButton:SetPoint("TOPRIGHT", -4, -4)
    frame.CloseButton:SetScript("OnClick", function() frame:Hide() end)

    frame.ClearButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    frame.ClearButton:SetSize(90, 24)
    frame.ClearButton:SetPoint("BOTTOMRIGHT", -16, 12)
    frame.ClearButton:SetText("Clear all")
    frame.ClearButton:SetScript("OnClick", function()
        PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_OFF)
        Queue:Clear()
    end)

    frame.Count = frame:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
    frame.Count:SetPoint("BOTTOMLEFT", 16, 18)

    frame.Empty = frame:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
    frame.Empty:SetPoint("TOPLEFT", 16, -50)
    frame.Empty:SetText("No dialogue queued.")

    frame.Scroll = CreateFrame("ScrollFrame", nil, frame, "UIPanelScrollFrameTemplate")
    frame.Scroll:SetPoint("TOPLEFT", 12, -42)
    frame.Scroll:SetPoint("BOTTOMRIGHT", -34, 46)
    frame.Content = CreateFrame("Frame", nil, frame.Scroll)
    frame.Content:SetWidth(PANEL_WIDTH - 46)
    frame.Scroll:SetScrollChild(frame.Content)

    self.rowPool = CreateFramePool("Button", frame.Content, nil, function(_, row)
        row:Hide()
        row:ClearAllPoints()
        row.item = nil
    end)
    return frame
end

local function InitRow(row)
    if row.Text then return end
    row:SetHeight(ROW_HEIGHT)
    row:SetWidth(PANEL_WIDTH - 46)
    row:SetHighlightTexture("Interface\\QuestFrame\\UI-QuestTitleHighlight", "ADD")

    row.Icon = row:CreateTexture(nil, "ARTWORK")
    row.Icon:SetSize(16, 16)
    row.Icon:SetPoint("LEFT", 4, 0)

    row.Remove = CreateFrame("Button", nil, row)
    row.Remove:SetSize(24, 24)
    row.Remove:SetPoint("RIGHT", -2, 0)
    row.Remove:SetNormalTexture(ns.mediaPath .. "BulletDelete")
    row.Remove:SetHighlightTexture("Interface\\BUTTONS\\UI-Panel-MinimizeButton-Highlight", "ADD")
    row.Remove:SetScript("OnClick", function()
        PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_OFF)
        if row.item then Queue:Remove(row.item) end
    end)
    row.Remove:SetScript("OnEnter", function(button)
        GameTooltip:SetOwner(button, "ANCHOR_RIGHT")
        GameTooltip:SetText("Remove this line")
        GameTooltip:Show()
    end)
    row.Remove:SetScript("OnLeave", GameTooltip_Hide)

    row.Text = row:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
    row.Text:SetJustifyH("LEFT")
    row.Text:SetWordWrap(false)
    row.Text:SetPoint("LEFT", row.Icon, "RIGHT", 8, 0)
    row.Text:SetPoint("RIGHT", row.Remove, "LEFT", -8, 0)

    row:SetScript("OnClick", function()
        PlaySound(SOUNDKIT.IG_MAINMENU_OPTION_CHECKBOX_ON)
        if row.item then
            Queue:MoveToFront(row.item)
            if Queue:IsPaused() then Queue:Resume() end
        end
    end)
    row:SetScript("OnEnter", function(self)
        if not self.item then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(self.item.title or self.item.name or "Dialogue")
        if self.item.name and self.item.title then
            GameTooltip:AddLine(self.item.name, 1, 1, 1)
        end
        local labels = { accept = "Quest offer", progress = "Quest progress", complete = "Quest turn-in" }
        GameTooltip:AddLine(labels[self.item.event] or "NPC dialogue", 0.7, 0.7, 0.7)
        GameTooltip:AddLine("Click to play now", 0.7, 0.7, 0.7)
        GameTooltip:Show()
    end)
    row:SetScript("OnLeave", GameTooltip_Hide)
end

function QueueList:Show()
    ns.db.showQueuePanel = true
    self:Update()
end

function QueueList:Toggle()
    ns.db.showQueuePanel = not ns.db.showQueuePanel
    self:Update()
end

function QueueList:Update()
    if not ns.db.showQueuePanel then
        if self.frame then self.frame:Hide() end
        return
    end
    local frame = self:GetFrame()
    self.rowPool:ReleaseAll()
    local total = Queue:Size()
    for index = 1, total do
        local item = Queue:Get(index)
        local row = self.rowPool:Acquire()
        InitRow(row)
        row.item = item
        row.Icon:SetTexture(ns.UI.TalkingHead.EventIcon(item))
        local label = item.title or item.name or "Dialogue"
        if item.name and item.title then
            label = format("%s  %s%s|r", label, GRAY_FONT_COLOR_CODE, item.name)
        end
        if index == 1 then
            label = (Queue:IsPaused() and "|cffffd100Paused: |r" or "|cffffd100Now: |r") .. label
        end
        row.Text:SetText(label)
        row:SetPoint("TOPLEFT", 0, -(index - 1) * ROW_HEIGHT)
        row:Show()
    end

    local visibleRows = math.max(1, math.min(total, MAX_VISIBLE_ROWS))
    frame:SetHeight(88 + visibleRows * ROW_HEIGHT)
    frame.Content:SetHeight(math.max(total, 1) * ROW_HEIGHT)
    frame.Scroll:SetVerticalScroll(math.min(frame.Scroll:GetVerticalScroll(), math.max(0, (total - visibleRows) * ROW_HEIGHT)))
    frame.Empty:SetShown(total == 0)
    frame.ClearButton:SetEnabled(total > 0)
    frame.Count:SetText(format("%d %s", total, ns.Util.Plural(total, "line")))
    frame:Show()
end

ns.OnInit(function()
    Queue:RegisterCallback("OnChanged", QueueList.Update, QueueList)
    QueueList:Update()
end)
