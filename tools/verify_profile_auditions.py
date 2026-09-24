"""Check actual render files and cache local ASR diagnostics for review."""
import difflib
import json
import re

import numpy as np
import soundfile as sf
import torch
from transformers import pipeline

import sys
from pathlib import Path

# Keep direct Windows helper invocations working alongside package entry points.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_profile_auditions import audio
from tools.prepare_profile_auditions import OUT, digest, save


def normalize(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())


def main():
    plan = json.loads((OUT/'performance-plan.json').read_text())
    path = OUT/'audio-verification.json'
    checks = json.loads(path.read_text()) if path.exists() else {'files':{}, 'note':'ASR catches content issues; it cannot certify natural acting or timbre.'}
    torch.set_num_threads(3)
    asr = None
    for row in plan['files']:
        wav = OUT/(row['base']+'.wav')
        if not wav.exists():
            continue
        sha = digest(wav)
        old = checks['files'].get(row['base'])
        if old and old['sha256']==sha:
            continue
        data, sr = sf.read(wav)
        assert np.isfinite(data).all() and np.max(abs(data)) <= .750001
        assert np.max(abs(data[-int(.49*sr):])) == 0
        assert len(data)/sr > 5
        if asr is None:
            asr = pipeline('automatic-speech-recognition', model='openai/whisper-small.en', device=-1)
        heard = asr({'raw':audio(wav,16000).astype(np.float32), 'sampling_rate':16000}, chunk_length_s=30)['text'].strip()
        expected_words, heard_words = normalize(row.get('synthesis_text',row['text'])), normalize(heard)
        differences = [{'type':tag,'expected':' '.join(expected_words[i:j]),'heard':' '.join(heard_words[a:b])}
                       for tag,i,j,a,b in difflib.SequenceMatcher(None,expected_words,heard_words,autojunk=False).get_opcodes() if tag!='equal']
        tail = data[-int(.60*sr):-int(.50*sr)]
        checks['files'][row['base']] = {'sha256':sha,'seconds':len(data)/sr,'sample_rate':sr,
             'peak':float(np.max(abs(data))),'finite':True,'silent_tail_seconds':.5,
             'last_generated_100ms_rms_db':float(20*np.log10(np.sqrt(np.mean(tail**2))+1e-12)),
             'asr':heard,'word_differences':differences}
        save(path,checks)
        print(row['base'],round(len(data)/sr,1),'seconds',json.dumps(differences),flush=True)
    print('CHECKED',len(checks['files']),'of',len(plan['files']),flush=True)


if __name__=='__main__':
    main()
