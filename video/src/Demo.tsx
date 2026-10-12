import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Audio, Img, Sequence, continueRender, delayRender, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from "remotion";
import vo from "../public/vo/vo.json";
import terminal from "../public/data/terminal.json";
import alerts from "../public/data/alerts.json";
import aria from "../public/shots/aria.json";

export const FPS = 30;
const LEAD = 6; // frames of picture before the voice starts
const TAIL = 14; // frames after it ends

// Jangkau's own palette (site/index.html), dark variant for the frame around real screens
const C = {
  bg: "#0f1626", panel: "#161f33", line: "#253049", ink: "#eef1f6", soft: "#aeb7c9",
  focus: "#ffd60a", pass: "#5fd39a", fail: "#ff8a80", navy: "#14213d",
};
const FONT = '"Atkinson Hyperlegible Next", system-ui, sans-serif';
const MONO = '"Atkinson Hyperlegible Mono", ui-monospace, monospace';

type Cap = { text: string; start: number; end: number };
type Scene = { name: string; text: string; duration: number; captions: Cap[] };
const SCENES = vo as Scene[];
const frames = (s: Scene) => Math.ceil(s.duration * FPS) + LEAD + TAIL;
export const totalFrames = SCENES.reduce((a, s) => a + frames(s), 0);
const scene = (name: string) => SCENES.find((s) => s.name === name)!;
// frame (inside its scene) where the phrase containing `words` starts being spoken
const cue = (name: string, words: string) => {
  const c = scene(name).captions.find((c) => c.text.includes(words));
  if (!c) throw new Error(`no caption "${words}" in ${name}`);
  return LEAD + Math.round(c.start * FPS);
};

// ---------- building blocks ----------

const useFonts = () => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;500;700;800&family=Atkinson+Hyperlegible+Mono:wght@400;600&display=block";
    document.head.appendChild(link);
    link.onload = () =>
      Promise.all([document.fonts.load(`700 40px "Atkinson Hyperlegible Next"`), document.fonts.load(`400 20px "Atkinson Hyperlegible Mono"`)])
        .then(() => continueRender(handle));
    link.onerror = () => continueRender(handle);
  }, [handle]);
};

type Rect = [number, number, number, number];
type Key = { at: number; cam?: Rect; ring?: Rect | null };

const ease = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.65, 0, 0.35, 1) });

/** A real screenshot behind a camera that glides between rects, with a keyboard-focus ring. */
const Shot: React.FC<{
  src: string; w: number; h: number; keys: Key[]; box?: Rect; label?: string; maxZoom?: number;
}> = ({ src, w, h, keys, box = [80, 56, 1760, 820], label, maxZoom = 1.7 }) => {
  const f = useCurrentFrame();
  const [bx, by, bw, bh] = box;
  const full: Rect = [0, 0, w, Math.min(h, (w * bh) / bw)];
  const camAt = (k: Key): Rect => k.cam ?? full;
  let i = 0;
  while (i + 1 < keys.length && keys[i + 1].at <= f) i++;
  const cur = keys[i], next = keys[i + 1];
  const prev = keys[i - 1];
  // glide over 24 frames into each key
  const t = ease(f, cur.at, cur.at + 24);
  const from = prev ? camAt(prev) : camAt(cur);
  const r = camAt(cur).map((v, j) => from[j] + (v - from[j]) * (i === 0 ? 1 : t)) as Rect;
  void next;
  // never zoom past maxZoom × "whole width fits": the screenshots are real pixels, not vectors
  const s = Math.min(bw / r[2], bh / r[3], (bw / w) * maxZoom);
  const tx = bw / 2 - (r[0] + r[2] / 2) * s;
  const ty = bh / 2 - (r[1] + r[3] / 2) * s;
  const ring = cur.ring;
  const ringIn = ease(f, cur.at + 14, cur.at + 30);
  const enter = spring({ frame: f, fps: FPS, config: { damping: 200 } });
  return (
    <div style={{
      position: "absolute", left: bx, top: by, width: bw, height: bh, overflow: "hidden", borderRadius: 18,
      background: "#fff", boxShadow: "0 40px 120px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.08)",
      transform: `translateY(${(1 - enter) * 40}px) scale(${0.97 + enter * 0.03})`, opacity: enter,
    }}>
      <div style={{ position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})` }}>
        <Img src={staticFile(src)} style={{ width: w, height: h, display: "block" }} />
        {ring && (
          <div style={{
            position: "absolute", left: ring[0] - 8 / s, top: ring[1] - 8 / s, width: ring[2] + 16 / s, height: ring[3] + 16 / s,
            border: `${5 / s}px solid ${C.focus}`, borderRadius: 10 / s, opacity: ringIn,
            boxShadow: `0 0 0 ${9999}px rgba(15,22,38,${0.42 * ringIn}), 0 0 ${30 / s}px ${C.focus}`,
          }} />
        )}
      </div>
      {label && <Tag style={{ position: "absolute", left: 20, top: 18 }}>{label}</Tag>}
    </div>
  );
};

const Tag: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; color?: string }> = ({ children, style, color = C.focus }) => (
  <div style={{
    fontFamily: FONT, fontWeight: 700, fontSize: 22, color: C.navy, background: color, padding: "6px 14px",
    borderRadius: 8, display: "inline-block", whiteSpace: "nowrap", ...style,
  }}>{children}</div>
);

/** Phrase-level captions, high contrast, with the spoken phrase underlined in focus yellow. */
const Captions: React.FC<{ s: Scene }> = ({ s }) => {
  const f = useCurrentFrame();
  const t = (f - LEAD) / FPS;
  const c = s.captions.find((c, i) => t >= c.start - 0.05 && t < (s.captions[i + 1]?.start ?? c.end + 0.6));
  if (!c) return null;
  const p = Math.min(1, Math.max(0, (t - c.start) / (c.end - c.start)));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 34, display: "flex", justifyContent: "center" }}>
      <div style={{
        fontFamily: FONT, fontWeight: 700, fontSize: 44, lineHeight: 1.25, color: "#fff", maxWidth: 1500, textAlign: "center",
        background: "rgba(10,15,28,.92)", padding: "14px 30px 18px", borderRadius: 14, position: "relative",
      }}>
        {c.text}
        <div style={{ position: "absolute", left: 30, bottom: 9, height: 5, borderRadius: 3, background: C.focus, width: `calc((100% - 60px) * ${p})` }} />
      </div>
    </div>
  );
};

const Big: React.FC<{ from: string; to: string; at: number; label: string; x?: number; y?: number; strike?: string }> = ({ from, to, at, label, x = 1200, y = 330, strike }) => {
  const f = useCurrentFrame();
  const a = spring({ frame: f - at, fps: FPS, config: { damping: 14, mass: 0.6 } });
  const b = spring({ frame: f - at - 14, fps: FPS, config: { damping: 12 } });
  if (f < at) return null;
  return (
    <div style={{
      position: "absolute", left: x, top: y, padding: "26px 40px", borderRadius: 22, background: "rgba(15,22,38,.94)",
      border: `2px solid ${C.line}`, fontFamily: FONT, color: C.ink, transform: `scale(${0.8 + 0.2 * a})`, opacity: a,
      boxShadow: "0 30px 80px rgba(0,0,0,.5)",
    }}>
      <div style={{ fontSize: 26, color: C.soft, fontWeight: 500 }}>{label}</div>
      <div style={{ fontSize: 120, fontWeight: 800, lineHeight: 1, letterSpacing: -2, display: "flex", alignItems: "baseline", gap: 26 }}>
        {strike && <span style={{ color: C.soft, fontSize: 64, textDecoration: "line-through", textDecorationThickness: 4 }}>{strike}</span>}
        <span style={{ color: C.fail }}>{from}</span>
        {to && <span style={{ color: C.soft, fontSize: 70 }}>→</span>}
        {to && <span style={{ color: C.pass, opacity: b, display: "inline-block", transform: `translateY(${(1 - b) * 20}px)` }}>{to}</span>}
      </div>
    </div>
  );
};

const Fade: React.FC<{ children: React.ReactNode; len: number }> = ({ children, len }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 8, len - 8, len], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

const Backdrop: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{
      background: `radial-gradient(1200px 700px at ${50 + Math.sin(f / 90) * 6}% ${40 + Math.cos(f / 110) * 5}%, #1b2742 0%, ${C.bg} 70%)`,
    }} />
  );
};

// ---------- scene-specific pieces ----------

/** What a screen reader gets: the page's real accessibility tree (Playwright aria snapshot). */
const AriaPanel: React.FC<{ tree: string; good?: boolean; box: Rect; title: string; perLine?: number; start?: number }> = ({ tree, good, box, title, perLine = 7, start = 10 }) => {
  const f = useCurrentFrame();
  const lines = tree.split("\n").filter((l) => !l.includes("/url:")).slice(0, 17);
  const shown = Math.max(0, Math.floor((f - start) / perLine));
  return (
    <div style={{
      position: "absolute", left: box[0], top: box[1], width: box[2], height: box[3], background: C.panel, borderRadius: 18,
      border: `1px solid ${C.line}`, padding: "22px 28px", fontFamily: MONO, fontSize: 21, color: C.soft, overflow: "hidden",
      boxShadow: "0 40px 120px rgba(0,0,0,.45)",
    }}>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 26, color: C.ink, marginBottom: 14 }}>{title}</div>
      {lines.slice(0, shown).map((l, i) => {
        const unnamed = /- (img|link|button)(:)?$/.test(l.trim()) || /^\s*- (img|link)\s*$/.test(l);
        const named = /- (img|link|button) "/.test(l) || /- (banner|navigation|main)/.test(l);
        return (
          <div key={i} style={{
            whiteSpace: "pre", lineHeight: 1.5,
            color: unnamed ? C.fail : named && good ? C.pass : C.soft, fontWeight: unnamed || (named && good) ? 600 : 400,
          }}>{l.replace("�", "-").slice(0, 52)}{unnamed ? "   ← no name" : ""}</div>
        );
      })}
    </div>
  );
};

const Terminal: React.FC<{ box: Rect; speed: number; start?: number }> = ({ box, speed, start = 4 }) => {
  const f = useCurrentFrame();
  const t = ((f - start) / FPS) * speed;
  const rows = (terminal as { t: number; text: string }[]).filter((r) => r.t <= t && !r.text.startsWith("neatlogs trace"));
  const head = "$ python jangkau.py demo_site/toko.html";
  return (
    <div style={{
      position: "absolute", left: box[0], top: box[1], width: box[2], height: box[3], background: "#0b1120", borderRadius: 18,
      border: `1px solid ${C.line}`, padding: "20px 26px", fontFamily: MONO, fontSize: 21, color: C.soft, overflow: "hidden",
      boxShadow: "0 40px 120px rgba(0,0,0,.5)", display: "flex", flexDirection: "column", justifyContent: "flex-end",
    }}>
      <div style={{ color: C.ink }}>{head}</div>
      {rows.slice(-19).map((r, i) => {
        const bad = r.text.includes("rejected");
        const good = r.text.includes("-> fixed");
        const done = r.text.startsWith("done:");
        return (
          <div key={i} style={{
            whiteSpace: "pre", overflow: "hidden", textOverflow: "ellipsis", lineHeight: 1.45,
            color: bad ? C.fail : good ? C.pass : done ? C.focus : C.soft, fontWeight: done || bad ? 600 : 400,
          }}>{r.text.replace(" (Fix any of the following:", "").slice(0, 92)}</div>
        );
      })}
    </div>
  );
};

const Bars: React.FC<{ at: number; box: Rect }> = ({ at, box }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const data = [["v1, no checks", 10], ["v2, first verifier", 14], ["v4, fixed check", 0]] as const;
  const o = spring({ frame: f - at, fps: FPS, config: { damping: 200 } });
  return (
    <div style={{
      position: "absolute", left: box[0], top: box[1], width: box[2], padding: "26px 32px", background: "rgba(15,22,38,.95)",
      borderRadius: 20, border: `2px solid ${C.line}`, fontFamily: FONT, color: C.ink, opacity: o, boxShadow: "0 30px 80px rgba(0,0,0,.5)",
    }}>
      <div style={{ fontSize: 26, fontWeight: 700, marginBottom: 6 }}>Failures left on the batik shop (of 47)</div>
      <div style={{ fontSize: 20, color: C.soft, marginBottom: 18 }}>same page, same model, traced in neatlogs</div>
      {data.map(([name, v], i) => {
        const g = spring({ frame: f - at - 8 - i * 8, fps: FPS, config: { damping: 200 } });
        return (
          <div key={name} style={{ display: "flex", alignItems: "center", gap: 16, margin: "12px 0" }}>
            <div style={{ width: 230, fontSize: 22, color: C.soft }}>{name}</div>
            <div style={{ height: 34, width: Math.max(6, (v / 47) * 900 * g), background: v ? C.fail : C.pass, borderRadius: 6 }} />
            <div style={{ fontSize: 30, fontWeight: 800, color: v ? C.fail : C.pass }}>{Math.round(v * g)}</div>
          </div>
        );
      })}
    </div>
  );
};

type Alert = { n: number; rule: string; sev: string; path: string; line: number; wcag: string[]; level: string | null; en: string[] };
const AlertList: React.FC<{ at: number; box: Rect }> = ({ at, box }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const list = (alerts as Alert[]).filter((a) => a.wcag.length).sort((a, b) => a.path.localeCompare(b.path) || a.line - b.line);
  const scroll = interpolate(f - at, [20, 220], [0, 360], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const o = spring({ frame: f - at, fps: FPS, config: { damping: 200 } });
  return (
    <div style={{
      position: "absolute", left: box[0], top: box[1], width: box[2], height: box[3], background: C.panel, borderRadius: 18,
      border: `1px solid ${C.line}`, fontFamily: FONT, color: C.ink, overflow: "hidden", opacity: o, boxShadow: "0 40px 120px rgba(0,0,0,.5)",
    }}>
      <div style={{ padding: "20px 26px", borderBottom: `1px solid ${C.line}`, background: C.panel, position: "relative", zIndex: 1 }}>
        <div style={{ fontSize: 28, fontWeight: 800 }}>Code scanning: {(alerts as Alert[]).length} open alerts</div>
        <div style={{ fontSize: 19, color: C.soft }}>live from the GitHub API for PugarHuda/jangkau, uploaded by the workflow as SARIF</div>
      </div>
      <div style={{ transform: `translateY(${-scroll}px)` }}>
        {list.slice(0, 22).map((a) => (
          <div key={a.n} style={{ display: "flex", alignItems: "center", gap: 14, padding: "13px 26px", borderBottom: `1px solid ${C.line}` }}>
            <div style={{ width: 12, height: 12, borderRadius: 6, background: a.sev === "error" ? C.fail : C.focus }} />
            <div style={{ fontFamily: MONO, fontSize: 20, width: 190 }}>{a.rule}</div>
            <div style={{ fontFamily: MONO, fontSize: 17, color: C.soft, flex: 1, whiteSpace: "nowrap" }}>{a.path.replace("demo_site/", "")}:{a.line}</div>
            <Tag style={{ fontSize: 17, padding: "3px 10px" }} color="#cfe1ff">WCAG {a.wcag.join(", ")} {a.level}</Tag>
            {a.en.length > 0 && <Tag style={{ fontSize: 17, padding: "3px 10px" }} color="#d9f5e6">EN {a.en.join(", ")}</Tag>}
          </div>
        ))}
      </div>
    </div>
  );
};

const Title: React.FC<{ at: number; children: React.ReactNode; sub?: string }> = ({ at, children, sub }) => {
  const f = useCurrentFrame();
  const a = spring({ frame: f - at, fps: FPS, config: { damping: 200 } });
  return (
    <div style={{ position: "absolute", left: 80, top: 34, fontFamily: FONT, color: C.ink, opacity: a, transform: `translateX(${(1 - a) * -20}px)` }}>
      <div style={{ fontSize: 30, fontWeight: 800 }}>{children}</div>
      {sub && <div style={{ fontSize: 22, color: C.soft }}>{sub}</div>}
    </div>
  );
};

// ---------- scenes ----------

const NL = { w: 1600, h: 900 };
const BOX_UNDER_TITLE: Rect = [80, 112, 1760, 790];

const scenesJsx: Record<string, (len: number) => React.ReactNode> = {
  problem: () => (
    <>
      <Shot src="shots/toko-before.png" w={2400} h={1671} box={[80, 70, 1020, 820]} label="A real shop page"
        keys={[{ at: 0, cam: [0, 0, 2400, 1930] }, { at: 160, cam: [0, 0, 1600, 1290] }, { at: 330, cam: [0, 380, 1600, 1290] }]} />
      <AriaPanel tree={aria["toko-before"]} box={[1140, 70, 700, 820]} title="What a screen reader gets" perLine={8} start={40} />
      <Big from="47" to="" at={cue("problem", "Forty-seven")} label="WCAG failures found by axe-core" x={240} y={560} />
      {(() => {
        const at = cue("problem", "Europe");
        return <Sequence from={at}><Tag style={{ position: "absolute", left: 1140, top: 26, fontSize: 24 }}>European Accessibility Act, in force since 28 June 2025</Tag></Sequence>;
      })()}
    </>
  ),
  agent: (len) => (
    <>
      <Title at={0} sub="a real run, replayed at 7× speed">Jangkau fixes the page, then proves it</Title>
      <Terminal box={[80, 112, 1000, 790]} speed={78 / ((len - 30) / FPS)} />
      <AriaPanel tree={aria["toko-after"]} good box={[1120, 112, 720, 790]} title="After: what a screen reader gets" perLine={6} start={30} />
    </>
  ),
  neatlogs: () => (
    <>
      <Title at={0} sub="every run is a trace: workflow, agent spans, tool spans, LLM calls">neatlogs</Title>
      <Sequence durationInFrames={cue("neatlogs", "then set up") + 10}>
        <Shot src="shots/nl-trace.png" {...NL} box={BOX_UNDER_TITLE} keys={[{ at: 0 }, { at: 30, cam: [470, 260, 730, 640], ring: [500, 300, 680, 230] }]} />
      </Sequence>
      <Sequence from={cue("neatlogs", "then set up")}>
        <Shot src="shots/nl-detections.png" {...NL} box={BOX_UNDER_TITLE} keys={[{ at: 0 }, { at: 40, cam: [70, 120, 1530, 330], ring: [86, 220, 1500, 44] }]} />
      </Sequence>
    </>
  ),
  incident1: () => (
    <>
      <Title at={0} sub="detection: Rule left unfixed · span: fix_rule (v2)">Incident 1: the verifier rejected correct fixes</Title>
      <Shot src="shots/nl-span-label.png" {...NL} box={BOX_UNDER_TITLE}
        keys={[{ at: 0 }, { at: 40, cam: [1030, 540, 565, 360], ring: [1050, 560, 520, 90] }, { at: cue("incident1", "The span"), cam: [1030, 720, 565, 180], ring: [1080, 836, 490, 26] },
          { at: cue("incident1", "We fixed"), cam: [0, 182, 1600, 718], ring: [1080, 836, 490, 26] }]} />
      <Bars at={cue("incident1", "We fixed") + 10} box={[110, 150, 860, 0]} />
    </>
  ),
  incident2: () => {
    const swap = cue("incident2", "Edge-map");
    return (
      <>
        <Title at={0} sub="StartBootstrap Freelancer, unmodified · detection: Rule left unfixed">Incident 2: contrast fixes kept failing</Title>
        <Sequence durationInFrames={swap + 10}>
          <Shot src="shots/nl-span-contrast.png" {...NL} box={BOX_UNDER_TITLE}
            keys={[{ at: 0 }, { at: 30, cam: [1030, 560, 565, 340], ring: [1085, 790, 330, 44] }, { at: cue("incident2", "hidden opacity"), cam: [1030, 740, 565, 160], ring: [1085, 838, 500, 60] }]} />
        </Sequence>
        <Sequence from={swap}>
          <Shot src="shots/freelancer-compare.png" w={860} h={800} box={[80, 112, 1060, 790]} keys={[{ at: 0, cam: [0, 0, 860, 800] }, { at: 60, cam: [0, 0, 860, 540] }]} />
          <Tag style={{ position: "absolute", left: 110, top: 128 }} color={C.fail}>before</Tag>
          <Tag style={{ position: "absolute", left: 640, top: 128 }} color={C.pass}>after</Tag>
          <Big from="33" to="0" at={20} label="failures, layout unchanged" x={1190} y={360} />
        </Sequence>
      </>
    );
  },
  incident3: () => {
    const swap = cue("incident3", "Now valid");
    return (
      <>
        <Title at={0} sub="W3C's inaccessible demo, fetched live · detection: Execution Failed">Incident 3: one bad edit threw away nineteen good ones</Title>
        <Sequence durationInFrames={swap + 10}>
          <Shot src="shots/nl-execfail.png" {...NL} box={BOX_UNDER_TITLE}
            keys={[{ at: 0 }, { at: 40, cam: [1030, 400, 565, 200], ring: [1045, 476, 535, 60] }]} />
        </Sequence>
        <Sequence from={swap}>
          <Shot src="shots/w3c-before.png" w={2400} h={1859} box={[80, 112, 860, 560]} label="before" keys={[{ at: 0, cam: [0, 0, 2400, 1560] }]} />
          <Shot src="shots/w3c-after.png" w={2400} h={1875} box={[980, 112, 860, 560]} label="after" keys={[{ at: 0, cam: [0, 0, 2400, 1560] }]} />
          <Big from="67" to="4" strike="26" at={12} label="failures: before the fix, 26 were left" x={460} y={640} />
        </Sequence>
      </>
    );
  },
  ci: () => (
    <>
      <Title at={0} sub="a composite GitHub Action; findings go to code scanning as SARIF">In CI on every push</Title>
      <Shot src="shots/gh-actions.png" w={2400} h={1350} box={[80, 112, 900, 790]}
        keys={[{ at: 0, cam: [540, 400, 1300, 800] }, { at: 30, cam: [540, 400, 1300, 800], ring: [560, 1105, 900, 66] }, { at: 110, cam: [540, 400, 1300, 800], ring: [560, 520, 900, 66] }]} />
      <AlertList at={cue("ci", "Every failure")} box={[1010, 112, 830, 790]} />
    </>
  ),
  entire: () => (
    <>
      <Title at={0} sub="each agent session saved as a checkpoint on the commit it produced">Entire</Title>
      <Shot src="shots/entire.png" w={2400} h={1350} box={BOX_UNDER_TITLE}
        keys={[{ at: 0 }, { at: 24, cam: [430, 280, 1460, 760], ring: [462, 450, 560, 30] }, { at: 90, cam: [430, 560, 1460, 760], ring: [520, 710, 1320, 160] }]} />
    </>
  ),
  cfo: () => (
    <>
      <Title at={0} sub="24-month model with Base, Growth and Downside scenarios">cfo.ai</Title>
      <Shot src="shots/cfo.png" w={2400} h={1350} box={BOX_UNDER_TITLE}
        keys={[{ at: 0 }, { at: 24, cam: [440, 230, 1940, 420], ring: [455, 320, 1900, 40] },
          { at: cue("cfo", "eighty-three"), cam: [440, 400, 1940, 260], ring: [480, 425, 1900, 50] },
          { at: cue("cfo", "downside"), cam: [440, 500, 1940, 140], ring: [480, 525, 1900, 40] }]} />
    </>
  ),
  outro: () => <Outro />,
};

const Outro: React.FC = () => {
    const f = useCurrentFrame();
    const a = spring({ frame: f, fps: FPS, config: { damping: 200 } });
    return (
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: FONT, color: C.ink }}>
        <div style={{ fontSize: 150, fontWeight: 800, letterSpacing: -3, opacity: a, outline: `6px solid ${C.focus}`, outlineOffset: 18, borderRadius: 8, padding: "0 30px" }}>Jangkau</div>
        <div style={{ fontSize: 40, color: C.soft, marginTop: 50, opacity: a }}>jangkau-jet.vercel.app · github.com/PugarHuda/jangkau</div>
      </AbsoluteFill>
    );
};

export const Demo: React.FC = () => {
  useFonts();
  let start = 0;
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <Backdrop />
      {SCENES.map((s) => {
        const len = frames(s);
        const from = start;
        start += len;
        return (
          <Sequence key={s.name} from={from} durationInFrames={len} name={s.name}>
            <Fade len={len}>{scenesJsx[s.name](len)}</Fade>
            <Sequence from={LEAD}><Audio src={staticFile(`vo/${s.name}.wav`)} /></Sequence>
            <Captions s={s} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
