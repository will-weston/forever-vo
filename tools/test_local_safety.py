"""Offline regression checks for local-generation input boundaries."""
import base64
import json
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch

import exportfile
from generate import Item, sound_path


class LocalSafetyTests(unittest.TestCase):
    def test_quest_event_cannot_be_a_path(self):
        with self.assertRaises(ValueError):
            Item('quests', '1', {'questID': 1, 'event': 'accept/../../outside'}, None)

    def test_audio_output_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                sound_path('Quests', '../../outside', sounds_dir=Path(folder))
            self.assertEqual(sound_path('Quests', '363-accept', sounds_dir=Path(folder)),
                             Path(folder) / 'Quests' / '363-accept.mp3')

    def test_import_rejects_invalid_quest_event(self):
        with self.assertRaises(ValueError):
            exportfile.to_capture({'lines': [{'k': 'quest', 'q': 1,
                'e': '../outside', 'x': 'Test'}]}, 'test')

    def test_import_decompression_is_bounded(self):
        data = {'v': 1, 'lines': [], 'padding': 'a' * 2048}
        encoded = 'FVO1:' + base64.b64encode(zlib.compress(json.dumps(data).encode())).decode()
        with patch.object(exportfile, 'MAX_EXPORT_BYTES', 1024):
            with self.assertRaises(ValueError):
                exportfile.decode(encoded)
        self.assertEqual(exportfile.decode(encoded), data)


if __name__ == '__main__':
    unittest.main()
