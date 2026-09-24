"""Regression checks for upstream integration with isolated Windows data."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import generate


class UpstreamMergeTests(unittest.TestCase):
    def test_bundled_captures_fill_gaps_but_local_text_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundled = root / 'tools/data'
            local = root / 'local'
            bundled.mkdir(parents=True)
            local.mkdir()
            (bundled / 'capture.json').write_text(json.dumps({'quests': {
                '1-accept': {'text': 'community', 'needs': 'f'},
                '2-accept': {'text': 'new Forever quest'},
            }}))
            (local / 'capture.json').write_text(json.dumps({'quests': {
                '1-accept': {'text': 'local correction'},
            }}))
            with patch.object(generate, '__file__', str(root / 'tools/generate.py')), \
                 patch.object(generate, 'DATA_DIR', local), \
                 patch.object(generate, 'CAPTURE_JSON', local / 'capture.json'):
                data = generate.load_sources()
            self.assertEqual(data['quests']['1-accept']['text'], 'local correction')
            self.assertEqual(data['quests']['2-accept']['text'], 'new Forever quest')

    def test_index_preserves_better_records_and_merges_only_dirty_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sound_index.json'
            good = {'d': 2, 'v': 'approved-profile', 't': 'approved-text'}
            target.write_text(json.dumps({'existing': good, 'other-worker': good, 'removed': good}))
            memory = {'existing': {'d': 99}, 'other-worker': {'d': 88}, 'new': good}
            dirty = {'existing', 'new', 'removed'}
            with patch.object(generate, 'SOUND_INDEX', target):
                generate.save_sound_index(memory, dirty)
            actual = json.loads(target.read_text())
            self.assertEqual(actual, {'existing': good, 'other-worker': good, 'new': good})
            self.assertFalse(dirty)

    def test_concurrent_index_writers_keep_every_record(self):
        worker = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from tools import generate
generate.SOUND_INDEX = Path(sys.argv[2])
for i in range(8):
    key = sys.argv[3] + '-' + str(i)
    generate.save_sound_index({key: {'d': 1, 'v': 'test', 't': key}}, {key})
"""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'sound_index.json'
            children = [subprocess.Popen([sys.executable, '-c', worker,
                        str(Path(__file__).resolve().parents[1]), str(target), str(i)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        for i in range(3)]
            try:
                for child in children:
                    _, error = child.communicate(timeout=30)
                    self.assertEqual(child.returncode, 0, error)
            finally:
                for child in children:
                    if child.poll() is None:
                        child.kill()
                        child.wait()
            self.assertEqual(len(json.loads(target.read_text())), 24)


if __name__ == '__main__':
    unittest.main()
