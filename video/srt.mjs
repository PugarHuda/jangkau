// Write out/jangkau-demo.srt from the same timings the video uses (LEAD/TAIL/FPS as in src/Demo.tsx).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

const FPS = 30, LEAD = 6, TAIL = 14;
const vo = JSON.parse(readFileSync("public/vo/vo.json", "utf8"));
const ts = (s) => {
  const ms = Math.round(s * 1000);
  const p = (n, w = 2) => String(n).padStart(w, "0");
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`;
};
let start = 0, n = 0;
const out = [];
for (const s of vo) {
  const base = (start + LEAD) / FPS;
  s.captions.forEach((c, i) => {
    const end = s.captions[i + 1]?.start ?? c.end + 0.4;
    out.push(`${++n}\n${ts(base + c.start)} --> ${ts(base + end)}\n${c.text}\n`);
  });
  start += Math.ceil(s.duration * FPS) + LEAD + TAIL;
}
mkdirSync("out", { recursive: true });
writeFileSync("out/jangkau-demo.srt", out.join("\n"));
console.log(`${n} cues`);
