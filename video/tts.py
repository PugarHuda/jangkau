"""Voice-over for the demo video: one wav per scene plus phrase timings for the subtitles.
Kokoro (open-weight TTS, runs locally). Each phrase is synthesised on its own, so subtitle timings are exact.
Setup: pip install kokoro-onnx soundfile; download kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases into $KOKORO_DIR. Run: python video/tts.py"""
import json
import os
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

VOICE, SPEED, SR = "af_heart", 1.05, 24000
PAUSE = {",": 0.12, ":": 0.2, ".": 0.32}  # silence after a phrase, by its last punctuation
OUT = Path(__file__).parent / "public" / "vo"
MODEL = Path(os.environ.get("KOKORO_DIR", "."))
# how a word is spoken, when the caption should keep its written form
SAY = {"Jangkau": "Jahng-cow", "cfo.ai": "C.F.O. dot A.I.", "neatlogs": "neat logs", "W3C's": "W 3 C's",
       "EN 301 549": "E N 3 0 1, 5 4 9", "CI": "C I", "WCAG": "W-cag", "Vercel": "Ver-sell"}

SCENES = [
    ("problem", "One in six people lives with a disability. To a screen reader, this online shop sounds like: "
                "image. Link. Image. Forty-seven accessibility failures. And in Europe, since June 2025, "
                "that's a legal problem."),
    ("agent", "Jangkau is an agent that doesn't just audit the page. It fixes it. Every edit is re-checked in a "
              "real browser, and if it breaks anything, it's rolled back and tried again."),
    ("neatlogs", "We traced every run with neatlogs, then set up a detection that flags each rule the agent "
                 "failed to fix. Here's what it caught."),
    ("incident1", "Incident one. Our first verifier rejected correct label fixes. The span told us why: it "
                  "counted rules still waiting in the queue as breakage. We fixed the check, and the shop went "
                  "from forty-seven failures to zero."),
    ("incident2", "Incident two, on a real Bootstrap template. Contrast fixes kept failing. The traces showed a "
                  "pixel diff punishing correct recolors, and then a hidden opacity of zero point six five. "
                  "Edge-map diffs, measured feedback, and escalation to a stronger model took it from "
                  "thirty-three to zero."),
    ("incident3", "Incident three, on the W3C's own inaccessible demo page. The Execution Failed detection caught "
                  "one bad edit throwing away nineteen good ones. Now valid edits are kept: sixty-seven "
                  "failures down to four."),
    ("ci", "It also runs in CI, as a GitHub Action. Every failure lands in code scanning, mapped to WCAG and to "
           "the European standard, EN 301 549."),
    ("trace", "Every fix is traceable. The fixed page carries a stamp that leads back to its neatlogs trace, and "
              "every Vercel deploy is re-checked before it gets a green status."),
    ("entire", "Entire recorded the coding sessions behind these fixes, as checkpoints on our commits."),
    ("cfo", "And cfo.ai modeled the business on measured costs: about nine cents per page, an eighty-four percent "
            "gross margin, and a downside case that set our per-page spend cap."),
    ("outro", "Jangkau. So the web reaches everyone."),
]


def phrases(text: str) -> list:
    return [p for p in re.split(r"(?<=[,.:])\s+", text) if p.strip(" ,.:")]


def spoken(phrase: str) -> str:
    for word, say in SAY.items():
        phrase = re.sub(rf"\b{re.escape(word)}(?=\W|$)", say, phrase)
    return phrase


def main():
    tts = Kokoro(str(MODEL / "kokoro-v1.0.onnx"), str(MODEL / "voices-v1.0.bin"))
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in SCENES:
        audio, caps, t = [], [], 0.0
        for ph in phrases(text):
            samples, _ = tts.create(spoken(ph), voice=VOICE, speed=SPEED, lang="en-us")
            samples = np.trim_zeros(samples, "fb")
            dur = len(samples) / SR
            caps.append({"text": ph, "start": round(t, 3), "end": round(t + dur, 3)})
            gap = PAUSE.get(ph[-1], 0.08)
            audio += [samples, np.zeros(int(gap * SR), dtype=samples.dtype)]
            t += dur + gap
        sf.write(OUT / f"{name}.wav", np.concatenate(audio), SR)
        out.append({"name": name, "text": text, "duration": round(t, 3), "captions": caps})
        print(f"{name:10} {t:5.1f}s")
    (OUT / "vo.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"total {sum(s['duration'] for s in out):.1f}s")


main()
