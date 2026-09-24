local _, ns = ...
local Util = ns.Util

--[[
Voice packs are separate addons that depend on ForeverVO and call
ForeverVO.RegisterPack(pack) with a table of this shape:

  {
    name = "Forever", version = "0.1", priority = 100,
    folder = "ForeverVO_Data",          -- Interface\AddOns\<folder>\Sounds\...
    quests = {
      [questID] = { a = 5.2, p = 2.0, c = 3.1, g = "a", npc = 288,
                    cP = { { d = 1.1 }, { d = 1.4, n = true }, { d = 0.6 } } },
      -- a/p/c: duration in seconds of accept/progress/complete audio (absent = no file)
      -- g: which of a/p/c exist as m-/f- variants, because $G branches per line
      --    ("a" = only the accept text branches). `true` means all of them, as
      --    packs built before this wrote it.
      -- wa/wp/wc: the pipeline still wants this event captured again, by a
      --    reader whose sex letter (m/f) is in the string: "f" when only a
      --    male character has read a line the client resolved a $G branch
      --    out of, "mf" when nobody knows who read it. The addon exports
      --    such a line even though it is voiced (Capture.lua, Export.lua).
      -- npc: quest giver speaker key (creature ID, negative for game objects);
      --    absent when an item starts the quest. ender: the turn-in speaker,
      --    only when it differs from the giver. The addon uses them for a text
      --    the client leaves unattributed (an item-started or shared quest, a
      --    turn-in at a game object); packs built before ender existed carry
      --    the first speaker of any event as npc.
      -- aP/pP/cP: the parts of a line that mixes the speaker and the narrator,
      --    in reading order, each with its duration; n marks the narrator's
      --    (a <stage direction>). Files are <questID>-p<i>-<event>.mp3.
    },
    gossip = {
      [speakerKey] = {
        { f = "288-1a2b3c4d", h = "1a2b3c4d", t = "original text", d = 4.5, g = true,
          n = { [1] = 4.7 },      -- duration per alternate narrator voice
          P = { { d = 2.0 }, { d = 1.1, n = true } },   -- parts, as aP above; files <f>-p<i> with
          nP = { [1] = { [2] = 1.2 } } },               -- the speaker before the hash: 288-p2-1a2b3c4d
      },
    },
    npcs = { [speakerKey] = "Name" },
    narratorVoices = { "human-female", "dwarf-male" },
    narrator = {
      [questID] = { [1] = { a = 5.4, c = 3.3, cP = { [2] = 1.2 } }, [2] = { a = 5.1 } },
      -- the same quest read in each alternate narrator voice, indexed into
      -- narratorVoices, with that recording's own durations; aP/pP/cP hold the
      -- durations of the narrator's parts of a mixed line, by part index
    },
  }

Files live at Sounds\Quests\<questID>-accept.mp3 (with m-/f- prefix when g is
set) and Sounds\Gossip\<f>.mp3. Higher priority packs are consulted first, so a
pack of new or revised lines can sit on top of a base pack.

Lines with no speaker to clone - quests and gossip from objects and items - use
the pack's default narration at the regular sound path. Alternate narrator
metadata from upstream packs is accepted but is not used for playback.

Mixed speaker/narrator lines can carry parts, played in order by the queue.
A line that is only a stage direction can have parts without a whole-line file.
]]

local Packs = {
    list = {},
    byName = {},
}
ns.Packs = Packs

local FUZZY_THRESHOLD = 0.6
local QUEST_FIELD = { accept = "a", progress = "p", complete = "c" }

function ns.RegisterPack(pack)
    assert(type(pack) == "table" and pack.name and pack.folder, "ForeverVO.RegisterPack: pack needs name and folder")
    if Packs.byName[pack.name] then
        ns.Print(format("voice pack %q registered twice, ignoring the second copy", pack.name))
        return
    end
    pack.priority = pack.priority or 0
    pack.quests = pack.quests or {}
    pack.gossip = pack.gossip or {}
    pack.npcs = pack.npcs or {}
    pack.nameToKey = {}
    for key, name in pairs(pack.npcs) do
        pack.nameToKey[name] = pack.nameToKey[name] or key
    end
    Packs.byName[pack.name] = pack
    table.insert(Packs.list, pack)
    table.sort(Packs.list, function(a, b)
        if a.priority ~= b.priority then
            return a.priority > b.priority
        end
        return a.name < b.name
    end)
    ns.Debug("registered pack", pack.name, pack.version or "")
    if ns.Queue then
        ns.Queue:TriggerEvent("OnPacksChanged")
    end
end

function Packs:Count()
    return #self.list
end

function Packs:Iterate()
    return ipairs(self.list)
end

local function SoundPath(pack, subfolder, base)
    return format("Interface\\AddOns\\%s\\Sounds\\%s\\%s.mp3", pack.folder, subfolder, base)
end

--- Resolve mixed speaker/narrator lines using the pack's default narration.
local function ResolveParts(pack, subfolder, base, parts)
    local head, last = base:match("^(.*)%-([^%-]+)$")
    local resolved, total = {}, 0
    for index, part in ipairs(parts) do
        local name = format("%s-p%d-%s", head, index, last)
        local seconds = part.d or 0
        resolved[index] = { path = SoundPath(pack, subfolder, name), duration = seconds }
        total = total + seconds
    end
    return resolved, total
end

--- Finds path, duration, pack and optional parts for a quest event. A parts-only
--- line uses its first part as the path so the queue can identify the line.
---@param questID number
---@param event "accept"|"progress"|"complete"
function Packs:FindQuest(questID, event)
    local field = QUEST_FIELD[event]
    if not questID or not field then
        return nil
    end
    for _, pack in ipairs(self.list) do
        local entry = pack.quests[questID]
        local parts = entry and entry[field .. "P"]
        if entry and (entry[field] or parts) then
            local base = format("%d-%s", questID, event)
            -- Accept both upstream's event letters and this fork's older
            -- ag/pg/cg flags. Legacy g=true still means all quest events.
            if entry.g == true or entry[field .. "g"]
                or (type(entry.g) == "string" and string.find(entry.g, field, 1, true)) then
                base = Util.PlayerGenderPrefix() .. base
            end
            if parts and #parts > 0 then
                local resolved, total = ResolveParts(pack, "Quests", base, parts)
                local path = entry[field] and SoundPath(pack, "Quests", base) or resolved[1].path
                return path, total, pack, resolved
            end
            return SoundPath(pack, "Quests", base), entry[field], pack
        end
    end
end

--- True when the pack that voices the quest event asks for it to be captured
--- again by a character of the player's sex (the wa/wp/wc fields): the
--- pipeline has only one gender's reading of a line the client resolves a
--- $G branch out of, or none it can trust, and this player can supply it.
---@param pack table the pack FindQuest found the event in
function Packs:QuestWanted(pack, questID, event)
    local field = QUEST_FIELD[event]
    local entry = pack and field and pack.quests[questID]
    local wanted = entry and entry["w" .. field]
    local letter = Util.PlayerSexLetter()
    return type(wanted) == "string" and letter ~= nil and strfind(wanted, letter, 1, true) ~= nil
end

--- Speaker key recorded by any pack for the quest: the giver, or for a
--- progress or complete text the turn-in speaker where the pack records one.
function Packs:QuestGiver(questID, event)
    local turnIn = event == "progress" or event == "complete"
    for _, pack in ipairs(self.list) do
        local entry = pack.quests[questID]
        local key = entry and ((turnIn and entry.ender) or entry.npc)
        if key then
            return key
        end
    end
end

function Packs:SpeakerName(key)
    if not key then
        return nil
    end
    for _, pack in ipairs(self.list) do
        local name = pack.npcs[key]
        if name then
            return name
        end
    end
end

function Packs:SpeakerKeyByName(name)
    if not name then
        return nil
    end
    for _, pack in ipairs(self.list) do
        local key = pack.nameToKey[name]
        if key then
            return key
        end
    end
end

--- Finds gossip/greeting audio for a speaker. Exact hash match first, then the
--- most similar text above the fuzzy threshold. Returns path, duration, pack.
---@param speakerKey number
---@param text string
function Packs:FindGossip(speakerKey, text)
    if not speakerKey or not text then
        return nil
    end
    -- Pack text carries the placeholders; the client has already expanded them
    -- in what we were handed. Tokenise once so both the hash and the fuzzy
    -- word sets compare like with like whoever is reading.
    local tokenized = Util.Tokenize(text)
    local hash = Util.TextKey(tokenized)
    local bestEntry, bestPack, bestScore

    for _, pack in ipairs(self.list) do
        local entries = pack.gossip[speakerKey]
        if entries then
            for _, entry in ipairs(entries) do
                if entry.h == hash then
                    bestEntry, bestPack, bestScore = entry, pack, 1
                    break
                end
            end
            if bestScore == 1 then
                break
            end
            for _, entry in ipairs(entries) do
                local score = Util.Similarity(tokenized, entry.t or "")
                if score >= FUZZY_THRESHOLD and (not bestScore or score > bestScore) then
                    bestEntry, bestPack, bestScore = entry, pack, score
                end
            end
        end
    end

    if not bestEntry then
        return nil
    end
    local base = bestEntry.f
    if bestEntry.g then
        base = Util.PlayerGenderPrefix() .. base
    end
    ns.Debug(format("gossip match %.2f for %s", bestScore, base))
    if bestEntry.P and #bestEntry.P > 0 then
        local resolved, total = ResolveParts(bestPack, "Gossip", base, bestEntry.P)
        local path = bestEntry.d and SoundPath(bestPack, "Gossip", base) or resolved[1].path
        return path, total, bestPack, resolved
    end
    return SoundPath(bestPack, "Gossip", base), bestEntry.d, bestPack
end
