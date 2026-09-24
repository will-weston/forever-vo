"""Generate a bounded batch for an undead warlock; never publishes anything."""
import argparse
import sqlite3

import sys
from pathlib import Path

# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.config import DATA_DIR
from tools.generate import main as generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    snapshots = list((DATA_DIR / 'classicdb').rglob('mangos.sqlite'))
    if not snapshots:
        parser.error('Run Run-Local.ps1 classicdb first')
    with sqlite3.connect(snapshots[0]) as db:
        quest_ids = {row[0] for row in db.execute(
            'SELECT entry FROM quest_template WHERE ZoneOrSort IN (85,154)')}
    # Undead starter/class quests through the level-10 voidwalker chain.
    quest_ids.update((3099, 1470, 1478, 1473, 1471))
    quest_ids.discard(5847)  # Original collector's-edition pet redemption, not leveling dialogue.
    options = ['--only', 'quests', '--limit', str(args.limit), '--narrator-voices', 'none']
    for quest_id in sorted(quest_ids):
        options.extend(('--quest', str(quest_id)))
    if args.dry_run:
        options.append('--dry-run')
    return generate(options)


if __name__ == '__main__':
    raise SystemExit(main())
