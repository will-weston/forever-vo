"""Validate staged or installed Lua 5.1 tables against the complete pack plan."""
import argparse
import json
import os
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[1]
STAGE=Path(os.environ.get('FOREVER_VO_PROFILE_STAGE',str(ROOT/'.local-state/profile-packs/tirisfal-20260923'))).resolve()


def tables(folder):
    lua=LuaRuntime()
    lua.execute('ForeverVO_DataPack = {}')
    for p in (folder/'Data').glob('*.lua'):
        lua.compile(p.read_text(encoding='utf-8'))
        if p.name in ('Quests.lua','NPCs.lua','Gossip.lua','Narrator.lua'):
            lua.execute(p.read_text(encoding='utf-8'))
    return lua,lua.globals().ForeverVO_DataPack


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pack',type=Path,required=True);args=ap.parse_args()
    plan=json.loads((STAGE/'plan.json').read_text());manifest=json.loads((STAGE/'manifest.json').read_text())
    engine,pack=tables(args.pack)
    events={}
    for row in plan['files']:
        key=(row['quest'],row['event']);events.setdefault(key,[]).append(row['base'])
        path=args.pack/'Sounds/Quests'/(row['base']+'.mp3');assert path.exists(),str(path)
    for (qid,event),bases in events.items():
        q=pack.quests[qid];assert q is not None,qid
        field={'accept':'a','progress':'p','complete':'c'}[event]
        expected=max(manifest['files'][base]['seconds'] for base in bases)
        assert abs(q[field]-expected)<.002,(qid,event,q[field],expected)
        if len(bases)==2:assert q[field+'g'] or q['g'],(qid,event,'missing gender flag')
    old_engine,old=tables(ROOT/'ForeverVO_Data')
    preserved=0
    for qid,record in old.quests.items():
        if qid in plan['quest_ids']:continue
        for k,v in record.items():assert pack.quests[qid][k]==v,(qid,k,'unrelated quest changed')
        preserved+=1
    print('PASS Lua 5.1: all',len(events),'quest stages and durations verified;',preserved,'unrelated quest records preserved')


if __name__=='__main__':main()
