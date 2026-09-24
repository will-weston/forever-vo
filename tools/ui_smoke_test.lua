-- Local smoke harness: real addon queue/UI code, mocked client widgets/audio.
local methods = {}
local function noop() end
for name in string.gmatch([[SetFrameStrata SetFrameLevel SetClampedToScreen SetMovable
RegisterForClicks RegisterForDrag RegisterEvent UnregisterEvent SetUserPlaced
StartMoving StopMovingOrSizing EnableMouse SetFontObject SetJustifyH SetJustifyV
SetAlpha SetColorTexture SetBlendMode SetAtlas SetTexture SetNormalTexture SetHighlightTexture
SetTextColor SetShadowColor SetBackdrop SetBackdropColor SetBackdropBorderColor
SetScale SetWordWrap SetPortraitZoom SetCamDistanceScale SetFacing SetCreature
ClearModel SetToFinalAlpha SetTarget SetFromAlpha SetToAlpha SetDuration SetStartDelay
SetOrder SetScaleFrom SetScaleTo SetOrigin AddLine]], '%S+') do methods[name] = noop end
function methods:SetSize(w,h) self.width,self.height=w,h end
function methods:SetWidth(w) self.width=w end
function methods:SetHeight(h) self.height=h end
function methods:SetPoint(...) self.points[#self.points+1]={...} end
function methods:SetAllPoints(target) self.allPoints=target end
function methods:AddMaskTexture(mask) self.mask=mask end
function methods:SetTitleOffsets(left,right) self.titleOffsets={left,right} end
function methods:SetAtlas(atlas) self.atlas=atlas end
function methods:SetColorTexture(...) self.atlas=nil; self.color={...} end
function methods:ClearAllPoints() self.points={} end
function methods:SetText(t) self.text=t end
function methods:SetAnimation(a) self.animation=a end
function methods:SetEnabled(v) self.enabled=v end
function methods:SetScript(n,f) self.scripts[n]=f end
function methods:GetFrameLevel() return 510 end
function methods:IsMouseOver() return false end
function methods:IsShown() return self.shown end
function methods:Show() self.shown=true end
function methods:Hide()
    local was=self.shown; self.shown=false
    if was and self.scripts.OnHide then self.scripts.OnHide(self) end
end
function methods:SetShown(v) if v then self:Show() else self:Hide() end end
function methods:Play() self.playing=true end
function methods:Stop() self.playing=false end
function methods:SetScrollChild(v) self.child=v end
function methods:SetVerticalScroll(v) self.scroll=v end
function methods:GetVerticalScroll() return self.scroll or 0 end
function methods:SetOwner(v) self.owner=v end
function methods:GetOwner() return self.owner end
function CreateFrame(kind,name,parent,template)
    local obj=setmetatable({kind=kind,parent=parent,template=template,scripts={},points={},shown=true},{__index=methods})
    if name then _G[name]=obj end
    if template=="UIPanelSquareButton" then obj.icon=CreateFrame("Texture") end
    if template=="PortraitFrameTemplate" then
        obj.PortraitContainer=CreateFrame('Frame',nil,obj)
        obj.PortraitContainer.portrait=CreateFrame('Texture',nil,obj.PortraitContainer)
        obj.PortraitContainer.CircleMask=CreateFrame('MaskTexture',nil,obj.PortraitContainer)
        obj.TitleContainer=CreateFrame('Frame',nil,obj)
        obj.TitleContainer.TitleText=CreateFrame('FontString',nil,obj.TitleContainer)
        obj.CloseButton=CreateFrame('Button',nil,obj)
    end
    return obj
end
function methods:CreateFontString() return CreateFrame('FontString') end
function methods:CreateTexture() return CreateFrame('Texture') end
function methods:CreateAnimationGroup() return CreateFrame('AnimationGroup') end
function methods:CreateAnimation() return CreateFrame('Animation') end
function CreateFramePool(kind,parent,template,reset)
    local pool={active={}}
    function pool:Acquire() local o=CreateFrame(kind,nil,parent,template); table.insert(self.active,o); return o end
    function pool:ReleaseAll() for _,o in ipairs(self.active) do reset(self,o) end; self.active={} end
    return pool
end
function CreateColor(r,g,b,a)
    return {GetRGB=function()return r,g,b end,GetRGBA=function()return r,g,b,a or 1 end}
end
function CopyTable(t) local out={}; for k,v in pairs(t) do out[k]=type(v)=='table' and CopyTable(v) or v end; return out end
function wipe(t) for k in pairs(t) do t[k]=nil end end
format=string.format
function strtrim(s) return s:match('^%s*(.-)%s*$') end
function PlaySound() end
function SquareButton_SetIcon(button,name) assert(name=="RIGHT"); button.icon.direction=name end
function UnitFactionGroup() return 'Horde' end
local units={questnpc='Creature-0-0-0-0-1569-1'}
function UnitExists(unit) return units[unit]~=nil end
function UnitGUID(unit) return units[unit] end
function UnitName(unit) return unit=='player' and 'Adventurer' or 'Test NPC' end
function UnitClass() return 'Warlock' end
function UnitRace() return 'Undead' end
function UnitSex() return 2 end
function SetPortraitTexture(texture,unit) texture.portraitGUID=units[unit] end
function strsplit(delimiter,text)
    local parts={}; for part in text:gmatch('[^'..delimiter..']+') do table.insert(parts,part) end
    return unpack(parts)
end
SOUNDKIT={}; UISpecialFrames={}; SlashCmdList={}; GRAY_FONT_COLOR_CODE='|cff888888'
UIParent=CreateFrame('Frame'); GameTooltip=CreateFrame('GameTooltip')
function GameTooltip_Hide() GameTooltip:Hide() end
C_Texture={GetAtlasExists=function()return true end}
C_AddOns={GetAddOnMetadata=function()return 'test' end}
CallbackRegistryMixin={}
function CallbackRegistryMixin:OnLoad() self.callbacks={} end
function CallbackRegistryMixin:GenerateCallbackEvents() end
function CallbackRegistryMixin:RegisterCallback(event,fn,owner)
    self.callbacks[event]=self.callbacks[event] or {}; table.insert(self.callbacks[event],{fn,owner})
end
function CallbackRegistryMixin:TriggerEvent(event,...)
    for _,cb in ipairs(self.callbacks[event] or {}) do cb[1](cb[2],...) end
end
function CreateFromMixins(t) return CopyTable(t) end
local now,timers=0,{}
C_Timer={}
function C_Timer.NewTimer(delay,fn)
    local t={at=now+delay,fn=fn,Cancel=function(self) self.cancelled=true end}; table.insert(timers,t); return t
end
C_Timer.After=C_Timer.NewTimer
local function advance(dt)
    local untilTime=now+dt
    while true do
        local first
        for _,t in ipairs(timers) do if not t.cancelled and t.at<=untilTime and (not first or t.at<first.at) then first=t end end
        if not first then break end
        now=first.at; first.cancelled=true; first.fn()
    end
    now=untilTime
end
Settings={VarType={Boolean='boolean',Number='number'},categories={},registered={}}
function Settings.RegisterVerticalLayoutCategory(name)
    local layout={rows={},AddInitializer=function(self,i)table.insert(self.rows,i)end}
    local c={name=name,layout=layout,GetID=function(self)return self.name end}
    table.insert(Settings.categories,c); return c,layout
end
function Settings.RegisterVerticalLayoutSubcategory(parent,name) return Settings.RegisterVerticalLayoutCategory(name) end
function Settings.RegisterAddOnSetting(category,id,key,db,kind,name,default)
    assert(not Settings.registered[id],id)
    local s={key=key,GetValue=function()return db[key] end,SetValue=function(self,v)db[key]=v;if self.changed then self.changed(self,v) end end,
        SetValueChangedCallback=function(self,fn)self.changed=fn end}
    Settings.registered[id]=s; return s
end
function Settings.RegisterProxySetting(category,id,kind,name,default,get,set)
    assert(not Settings.registered[id],id)
    local s={GetValue=get,SetValue=function(_,v)set(v)end};Settings.registered[id]=s;return s
end
function Settings.CreateCheckbox(c,s) c.layout:AddInitializer(s) end
Settings.CreateDropdown=Settings.CreateCheckbox; Settings.CreateSlider=Settings.CreateCheckbox
function Settings.CreateSliderOptions() return {SetLabelFormatter=noop} end
function Settings.RegisterAddOnCategory() end
function Settings.OpenToCategory(id) Settings.opened=id end
function CreateSettingsListSectionHeaderInitializer(name) return {header=name} end
function CreateSettingsButtonInitializer(name,text,fn,tooltip,search) assert(search~=nil); return {button=name,click=fn} end
MinimalSliderWithSteppersMixin={Label={Right=1}}
local conversation='Speak quickly. The dead do not rest.'
C_GossipInfo={GetText=function()return conversation end,GetOptions=function()return {} end}
C_QuestLog={}
function GetGreetingText() return conversation end
function hooksecurefunc() end
local ns={}
local function load(path) assert(loadfile('ForeverVO/'..path))('ForeverVO',ns) end
load('Core/Init.lua');ns.db=CopyTable(ns.defaults);ns.char=CopyTable(ns.charDefaults)
ns.Print=noop;ns.Debug=noop
ns.Audio={IsEnabled=function()return true end,Exists=function()return true end,
    Play=function(path)return path end,Stop=noop,Idle=noop}
local captured={}
ns.Capture={Record=function(_,line)table.insert(captured,line)end}
ns.UI.MinimapButton={ApplySettings=noop}
load('Core/Util.lua');load('Core/Packs.lua');load('Core/Queue.lua');load('Core/Events.lua')
load('UI/TalkingHead.lua');load('Core/Settings.lua');load('Core/Commands.lua')
for _,init in ipairs(ns.initializers) do init() end
local Q,H=ns.Queue,ns.UI.TalkingHead
local function click(b) assert(b.enabled~=false); b.scripts.OnClick(b) end
local function item(i) return {path='voice'..i,kind='quest',event='accept',duration=100,name='Sarvis',speakerKey=1569,title='Quest '..i,
    text=string.rep('The Scourge will never rest. ',45)} end
assert(#Settings.categories==2 and Settings.categories[2].name=='Advanced')
local settingCount=0;for _ in pairs(Settings.registered)do settingCount=settingCount+1 end;assert(settingCount==15, "setting count: "..settingCount)
assert(#Settings.categories[1].layout.rows==10) -- 8 choices and 2 headings
for _,key in ipairs({'playGreeting','playGossip','gossipFrequency','narratorVoice','factionHead','showQueuePanel'}) do
    assert(not Settings.registered['FVO_'..key],key..' is still exposed')
end
for _,category in ipairs(Settings.categories) do
    for _,row in ipairs(category.layout.rows) do assert(row.button~='Playback queue') end
end
print('PASS: simplified settings initialize without removed dialogue, narrator, style, or queue controls')
local a,b,c=item(1),item(2),item(3);Q:Add(a);Q:Add(b);Q:Add(c)
click(H.frame.CloseButton);assert(Q:Current()==b and Q:Size()==2);advance(.3)
assert(H.displayed==b and H.frame.SkipButton.enabled and H.frame.QueueButton==nil)
print('PASS: X skips only the current line and continues the remaining queue')
advance(32);local pausedText=H.frame.Text.text;assert(#H.pageTimers>0)
click(H.frame.PauseButton);assert(Q:IsPaused() and not Q:IsPlaying() and #H.pageTimers==0 and H.frame.Model==nil and H.activePortrait:IsShown())
advance(40);assert(H.frame.Text.text==pausedText and H.frame.PauseButton.text=="Play")
click(H.frame.PauseButton);assert(Q:IsPlaying() and not Q:IsPaused() and H.frame.Text.text==ns.Util.Paginate(b.text,330)[1])
assert(H.frame.PauseButton.text=="Pause")
print('PASS: pause/play label follows audio state; subtitles pause and static portrait remains visible')
Q:Pause();click(H.frame.SkipButton);advance(.3);assert(Q:Current()==c and Q:IsPaused() and #H.pageTimers==0 and H.frame.SkipButton.enabled)
click(H.frame.SkipButton);assert(Q:IsEmpty() and H.frame.PauseButton.enabled==false and H.frame.SkipButton.enabled==false)
print('PASS: skipping while paused preserves pause; last line disables playback controls')
Q:Resume()
local menu={}
local root={CreateTitle=noop,CreateCheckbox=noop,CreateButton=function(_,label,fn)menu[label]=fn end}
MenuUtil={CreateContextMenu=function(_,build)build(nil,root)end}
ForeverVO_OnCompartmentClick(nil,'RightButton')
assert(menu.Pause and menu['Skip current line'] and menu.Options)
for label in pairs(menu) do assert(not label:lower():find('queue')) end
SlashCmdList.FOREVERVO('queue');SlashCmdList.FOREVERVO('narrator')
assert(ns.UI.QueueList==nil and ForeverVOQueueList==nil)
print('PASS: minimap playback menu and old slash commands never open a queue window')
ns.db.factionHead=false;H:ApplySettings()
assert(H.frame.TextBackground.atlas=='QuestBG-Parchment')
print('PASS: old background preference cannot override the quest parchment')
local first=item(100);Q:Add(first)
local firstPortrait=H.activePortrait
assert(firstPortrait.portraitGUID=='Creature-0-0-0-0-1569-1')
units.questnpc='Creature-0-0-0-0-1568-2'
local second=item(101);second.name='Mordo';second.speakerKey=1568;Q:Add(second)
local secondPortrait=H.portraits[1568]
assert(secondPortrait and not secondPortrait:IsShown() and H.activePortrait==firstPortrait)
units.questnpc=nil;units.target='Creature-0-0-0-0-9999-3'
Q:Skip();assert(H.activePortrait==secondPortrait and secondPortrait:IsShown() and not firstPortrait:IsShown())
assert(secondPortrait.portraitGUID=='Creature-0-0-0-0-1568-2' and secondPortrait.mask==H.frame.PortraitContainer.CircleMask)
Q:Pause();Q:Resume();assert(H.activePortrait==secondPortrait)
local narrator=item(102);narrator.speakerKey=-123;Q:Add(narrator);Q:Skip()
assert(H.activePortrait==nil and H.frame.Portrait:IsShown() and not secondPortrait:IsShown())
local unavailable=item(103);unavailable.speakerKey=9998;Q:Add(unavailable);Q:Skip()
assert(H.activePortrait==nil and H.frame.Portrait:IsShown() and H.portraits[9999]==nil)
Q:Clear();H.frame.Close.scripts.OnFinished();assert(not H.frame:IsShown())
units.questnpc='Creature-0-0-0-0-1568-2'
local replay=item(104);replay.speakerKey=1568;Q:Add(replay)
assert(H.activePortrait==secondPortrait and H.frame:IsShown())
H.frame.CloseButton.scripts.OnEnter(H.frame.CloseButton);assert(GameTooltip.text=='Close')
assert(H.frame.TextBackground.atlas=='QuestBG-Parchment' and H.frame.template=='PortraitFrameTemplate')
print('PASS: cached circular portraits survive walking away, speaker changes, pause/resume, and reopening; unknown speakers use the book')
Q:Clear()

-- Existing saved preferences must not silently suppress or change narration
-- after the controls for those preferences have been removed.
ns.db.playGreeting=false;ns.db.playGossip=false;ns.db.gossipFrequency='never'
ns.db.narratorVoice='dwarf-male';ns.db.showQueuePanel=true
ns.char.seenGossip={[units.questnpc]=true}
local pack={name='Smoke',folder='SmokePack',npcs={[1568]='Test NPC'},
    quests={[1]={a=2,c=3,ag=true,npc=-123}},
    gossip={[1568]={{f='test-greeting',h=ns.Util.TextKey(conversation),t=conversation,d=2,n={[1]=9}}}},
    narratorVoices={'dwarf-male'},narrator={[1]={[1]={a=9,c=10}}}}
ns.RegisterPack(pack)
local path,duration=ns.Packs:FindQuest(1,'accept')
assert(path=='Interface\\AddOns\\SmokePack\\Sounds\\Quests\\m-1-accept.mp3' and duration==2)
path,duration=ns.Packs:FindQuest(1,'complete')
assert(path=='Interface\\AddOns\\SmokePack\\Sounds\\Quests\\1-complete.mp3' and duration==3)
path,duration=ns.Packs:FindGossip(1568,conversation)
assert(path=='Interface\\AddOns\\SmokePack\\Sounds\\Gossip\\test-greeting.mp3' and duration==2)
print('PASS: object quests and conversation use default recordings and durations despite an old narrator preference')

ns.Events.GOSSIP_SHOW();assert(Q:Size()==1 and Q:IsPlaying())
ns.Events.GOSSIP_SHOW();assert(Q:Size()==1) -- Duplicate open events do not stack.
click(H.frame.SkipButton);assert(Q:IsEmpty())
ns.Events.GOSSIP_SHOW();assert(Q:Size()==1 and Q:IsPlaying()) -- A later visit can repeat.
advance(3);assert(Q:IsEmpty())
ns.Events.QUEST_GREETING();assert(Q:Current().event=='greeting')
Q:Clear()
Q:Add(item(200));ns.Events.GOSSIP_SHOW();assert(Q:Size()==1 and Q:Current().kind=='quest')
Q:Clear();ns.Events.GOSSIP_SHOW();assert(Q:Current().kind=='gossip')
ns.db.stopOnClose=true;ns.Events.GOSSIP_CLOSED();assert(Q:IsEmpty())
conversation='Missing audio is still captured for later generation.'
ns.Events.GOSSIP_SHOW();assert(Q:IsEmpty() and captured[#captured].found==false)
print('PASS: repeat dialogue, greeting playback, deduplication, quest priority, close behavior, and missing-audio capture remain functional')
