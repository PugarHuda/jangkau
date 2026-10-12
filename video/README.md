# Demo video

Every frame comes from real output, nothing is mocked:

- `capture.py`: Playwright screenshots of the real pages (shop before/after, W3C demo, landing, GitHub Actions,
  Entire, cfo.ai) plus the shop's real accessibility tree before and after (`aria_snapshot`).
- `capture/terminal.json`: timed stdout of a real `jangkau.py demo_site/shop.html` run (47 → 0, trace `6e973c4e…`).
- `public/shots/nl-*.png`: the neatlogs dashboard (trace, detections, flagged spans), captured logged in.
- `public/data/alerts.json`: open code scanning alerts from the GitHub API, with the WCAG / EN 301 549 mapping from the SARIF.
- `tts.py`: voice-over with Kokoro (open-weight TTS, local). Each phrase is synthesised on its own, so captions are exact.
- `src/Demo.tsx`: the Remotion composition. A yellow keyboard-focus ring moves through each real screen.

```bash
python capture.py                              # from the repo root venv
KOKORO_DIR=... python tts.py                   # needs kokoro-onnx + model files, see the docstring
npm install && npm run render                  # out/jangkau-demo.mp4
node srt.mjs                                   # out/jangkau-demo.srt
```
