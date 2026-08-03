import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";

export const WIDTH = 1920;
export const HEIGHT = 1080;
export const FPS = 30;
export const CHAPTER = 900; // 30s per chapter
export const DURATION_IN_FRAMES = 6 * CHAPTER; // 180s

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const mix = (a: string, b: string, t: number): string => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(v + (pb[i] - v) * Math.min(1, Math.max(0, t)))).join(",")})`;
};

// ── Camera: continuous inside a chapter (chains stay seamless); settles at ends.
const useChapter = () => {
  const f = useCurrentFrame();
  const c = Math.min(5, Math.floor(f / CHAPTER));
  const lf = f - c * CHAPTER;
  const t = lf / CHAPTER; // 0..1 through the chapter
  const cam = interpolate(t, [0, 1], [0, 1], { easing: Easing.inOut(Easing.sin) });
  return { f, c, lf, t, cam };
};

// Parallax wrapper: depth 0 (far) → 1 (near). Camera pans right; near layers move more.
// Far layers get slight blur (DOF), near foreground gets more — the 2.5D depth cue.
const Layer: React.FC<{
  depth: number; cam: number; children: React.ReactNode; blur?: number; pan?: number;
}> = ({ depth, cam, children, blur, pan = 420 }) => (
  <AbsoluteFill
    style={{
      transform: `translateX(${-cam * pan * (0.25 + depth)}px) scale(${1 + depth * 0.06})`,
      transformOrigin: "50% 70%",
      filter: blur ? `blur(${blur}px)` : undefined,
    }}
  >
    {children}
  </AbsoluteFill>
);

// ── Shared atmosphere ───────────────────────────────────────────────────────

const Sky: React.FC<{ top: string; mid: string; bot: string }> = ({ top, mid, bot }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, ${top} 0%, ${mid} 55%, ${bot} 100%)` }} />
);

const SunGlow: React.FC<{ x: number; y: number; r: number; color: string; halo?: number }> = ({ x, y, r, color, halo = 3.2 }) => (
  <div style={{ position: "absolute", left: x - r * halo, top: y - r * halo }}>
    <div style={{
      width: r * halo * 2, height: r * halo * 2, borderRadius: "50%",
      background: `radial-gradient(circle, ${color} 0%, ${color}55 ${Math.round(100 / halo)}%, transparent 70%)`,
    }} />
    <div style={{
      position: "absolute", left: r * (halo - 1), top: r * (halo - 1),
      width: r * 2, height: r * 2, borderRadius: "50%", background: color,
    }} />
  </div>
);

const Cloudbank: React.FC<{ y: number; scale: number; speed: number; seed: number; f: number; tint?: string; op?: number }> = ({
  y, scale, speed, seed, f, tint = "#FFFFFF", op = 0.9,
}) => {
  const x = ((seed * 731 + f * speed) % (WIDTH + 900)) - 700;
  return (
    <svg style={{ position: "absolute", left: x, top: y, opacity: op }} width={520 * scale} height={160 * scale} viewBox="0 0 520 160">
      <g fill={tint}>
        <ellipse cx={120} cy={110} rx={110} ry={44} />
        <ellipse cx={250} cy={80} rx={130} ry={58} />
        <ellipse cx={395} cy={108} rx={105} ry={42} />
      </g>
    </svg>
  );
};

const Birds: React.FC<{ f: number; y: number; speed: number; seed: number; count?: number; color?: string }> = ({
  f, y, speed, seed, count = 5, color = "#2B2B33",
}) => {
  const x = ((seed * 517 + f * speed) % (WIDTH + 700)) - 500;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={340} height={130} viewBox="0 0 340 130">
      {Array.from({ length: count }, (_, i) => {
        const wing = Math.sin(f / 4 + i) * 12;
        const bx = (i % 3) * 100 + (i > 2 ? 50 : 0);
        const by = Math.floor(i / 3) * 55 + Math.sin(f / 17 + i * 2) * 6;
        return (
          <path key={i} d={`M ${bx} ${by + 30} Q ${bx + 22} ${by + 30 - wing} ${bx + 44} ${by + 30}
                            M ${bx + 44} ${by + 30} Q ${bx + 66} ${by + 30 - wing} ${bx + 88} ${by + 30}`}
            stroke={color} strokeWidth={6} fill="none" strokeLinecap="round" />
        );
      })}
    </svg>
  );
};

// Volumetric light shafts (forest / underwater).
const Shafts: React.FC<{ f: number; color: string; n?: number; op?: number }> = ({ f, color, n = 5, op = 0.35 }) => (
  <AbsoluteFill style={{ overflow: "hidden" }}>
    {Array.from({ length: n }, (_, i) => (
      <div key={i} style={{
        position: "absolute",
        left: 150 + i * 380 + Math.sin(f / 90 + i * 2) * 30,
        top: -220, width: 190, height: HEIGHT + 400,
        background: `linear-gradient(180deg, ${color} 0%, transparent 88%)`,
        opacity: op * (0.7 + 0.3 * Math.sin(f / 60 + i * 3)),
        transform: `rotate(${11 + i * 1.5}deg)`, filter: "blur(14px)",
      }} />
    ))}
  </AbsoluteFill>
);

const Grade: React.FC<{ tint: string; strength?: number }> = ({ tint, strength = 0.14 }) => (
  <>
    <AbsoluteFill style={{ background: tint, opacity: strength, mixBlendMode: "soft-light" as const }} />
    <AbsoluteFill style={{
      background: "radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 58%, rgba(8,10,22,0.34) 100%)",
    }} />
  </>
);

// Cinema letterbox + doc-style lower third.
const DocChrome: React.FC<{ chapter: number; title: string; lf: number }> = ({ chapter, title, lf }) => {
  const show = lf > 40 && lf < 220;
  const a = interpolate(lf, [40, 70, 190, 220], [0, 1, 1, 0], clamp);
  return (
    <>
      <div style={{ position: "absolute", top: 0, width: "100%", height: 72, background: "#05060A" }} />
      <div style={{ position: "absolute", bottom: 0, width: "100%", height: 72, background: "#05060A" }} />
      {show && (
        <div style={{ position: "absolute", bottom: 108, left: 96, opacity: a, transform: `translateY(${(1 - a) * 14}px)` }}>
          <div style={{ fontFamily: "'Liberation Sans', Arial, sans-serif", fontWeight: 700, fontSize: 26,
            letterSpacing: 8, color: "#EDE6D6", opacity: 0.85 }}>
            CHAPTER {["I", "II", "III", "IV", "V", "VI"][chapter]}
          </div>
          <div style={{ fontFamily: "'Liberation Sans', Arial, sans-serif", fontWeight: 800, fontSize: 54,
            color: "#FFFFFF", textShadow: "0 3px 14px rgba(0,0,0,0.5)" }}>
            {title}
          </div>
          <div style={{ width: 92, height: 5, background: "#E8B44A", marginTop: 12, borderRadius: 3 }} />
        </div>
      )}
    </>
  );
};

// ── Creatures (rounded, soft — the house 'Pixar-ish' look) ──────────────────

const Giraffe: React.FC<{ x: number; y: number; f: number; scale?: number }> = ({ x, y, f, scale = 1 }) => {
  const step = Math.sin(f / 12) * 9;
  const nod = Math.sin(f / 26) * 3;
  return (
    <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${scale})` }} width={260} height={420} viewBox="0 0 260 420">
      <g stroke="#C98F3F" strokeWidth={20} strokeLinecap="round">
        <line x1={95} y1={330} x2={95 - step} y2={408} />
        <line x1={150} y1={335} x2={150 + step} y2={408} />
        <line x1={190} y1={330} x2={190 - step * 0.7} y2={408} />
      </g>
      <ellipse cx={145} cy={310} rx={82} ry={48} fill="#D9A24E" />
      <path d={`M 92 300 Q 60 210 74 120`} stroke="#D9A24E" strokeWidth={34} fill="none" strokeLinecap="round" />
      <g transform={`translate(70 ${104 + nod})`}>
        <ellipse rx={34} ry={26} fill="#D9A24E" />
        <ellipse cx={-26} cy={6} rx={13} ry={9} fill="#C08A3E" />
        <circle cx={6} cy={-8} r={6.5} fill="#3A2A12" />
        <line x1={10} y1={-24} x2={12} y2={-40} stroke="#C08A3E" strokeWidth={6} strokeLinecap="round" />
        <circle cx={12} cy={-44} r={6} fill="#8A5A24" />
      </g>
      {[0, 1, 2, 3].map((i) => (
        <circle key={i} cx={115 + i * 26} cy={296 + (i % 2) * 22} r={9} fill="#B97F3A" opacity={0.8} />
      ))}
      <path d={`M 222 300 Q 244 316 240 ${338 + Math.sin(f / 15) * 6}`} stroke="#C98F3F" strokeWidth={9} fill="none" strokeLinecap="round" />
    </svg>
  );
};

const Elephant: React.FC<{ x: number; y: number; f: number; scale?: number }> = ({ x, y, f, scale = 1 }) => {
  const step = Math.sin(f / 14 + 2) * 7;
  const trunk = Math.sin(f / 20) * 10;
  return (
    <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${scale})` }} width={340} height={260} viewBox="0 0 340 260">
      <g stroke="#8E97A8" strokeWidth={30} strokeLinecap="round">
        <line x1={120} y1={170} x2={120 - step} y2={246} />
        <line x1={185} y1={175} x2={185 + step} y2={246} />
        <line x1={245} y1={170} x2={245 - step * 0.6} y2={246} />
      </g>
      <ellipse cx={185} cy={135} rx={118} ry={78} fill="#9AA3B4" />
      <g transform="translate(72 100)">
        <circle r={52} fill="#9AA3B4" />
        <ellipse cx={26} cy={-6} rx={30} ry={40} fill="#8E97A8" opacity={0.85} />
        <circle cx={-16} cy={-12} r={7} fill="#2E3440" />
        <path d={`M -34 18 Q -66 ${46 + trunk} -50 ${92 + trunk * 1.6} Q -46 ${104 + trunk * 1.6} -34 ${100 + trunk * 1.4}`}
          stroke="#9AA3B4" strokeWidth={22} fill="none" strokeLinecap="round" />
      </g>
      <path d={`M 296 120 Q 316 132 310 ${152 + Math.sin(f / 13) * 5}`} stroke="#8E97A8" strokeWidth={8} fill="none" strokeLinecap="round" />
    </svg>
  );
};

const Deer: React.FC<{ x: number; y: number; f: number; scale?: number }> = ({ x, y, f, scale = 1 }) => {
  const step = Math.sin(f / 11) * 8;
  return (
    <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${scale})` }} width={230} height={230} viewBox="0 0 230 230">
      <g stroke="#8A6238" strokeWidth={13} strokeLinecap="round">
        <line x1={80} y1={150} x2={80 - step} y2={218} />
        <line x1={118} y1={155} x2={118 + step} y2={218} />
        <line x1={152} y1={150} x2={152 - step * 0.7} y2={218} />
      </g>
      <ellipse cx={115} cy={130} rx={62} ry={38} fill="#A5763F" />
      <path d="M 70 120 Q 52 88 58 62" stroke="#A5763F" strokeWidth={20} fill="none" strokeLinecap="round" />
      <g transform="translate(56 52)">
        <ellipse rx={22} ry={17} fill="#A5763F" />
        <circle cx={-8} cy={-4} r={4.5} fill="#33220E" />
        <path d="M 6 -14 L 2 -34 M 2 -26 L -8 -34 M 2 -26 L 12 -36" stroke="#7A5228" strokeWidth={5} fill="none" strokeLinecap="round" />
        <path d="M 14 -12 L 18 -30 M 16 -24 L 26 -32" stroke="#7A5228" strokeWidth={5} fill="none" strokeLinecap="round" />
      </g>
      <circle cx={172} cy={118} r={9} fill="#EDE0CC" />
      {[0, 1, 2].map((i) => <circle key={i} cx={104 + i * 20} cy={118} r={5} fill="#EDE0CC" opacity={0.8} />)}
    </svg>
  );
};

const Heron: React.FC<{ x: number; y: number; f: number }> = ({ x, y, f }) => {
  const peck = Math.max(0, Math.sin(f / 40)) * 14;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={150} height={230} viewBox="0 0 150 230">
      <line x1={70} y1={150} x2={70} y2={222} stroke="#5A6B78" strokeWidth={7} />
      <line x1={86} y1={150} x2={90} y2={222} stroke="#5A6B78" strokeWidth={7} />
      <ellipse cx={78} cy={128} rx={40} ry={28} fill="#8FA6B8" />
      <path d={`M 52 112 Q 34 ${76 + peck} 44 ${52 + peck}`} stroke="#8FA6B8" strokeWidth={13} fill="none" strokeLinecap="round" />
      <g transform={`translate(44 ${46 + peck})`}>
        <circle r={13} fill="#8FA6B8" />
        <circle cx={-3} cy={-3} r={3.5} fill="#1F2833" />
        <path d="M -12 2 L -38 8 L -12 8 Z" fill="#E8B44A" />
      </g>
    </svg>
  );
};

const Fish2: React.FC<{ f: number; seed: number; baseX: number; baseY: number }> = ({ f, seed, baseX, baseY }) => {
  // Periodic jump arc out of the river.
  const period = 220 + seed * 40;
  const p = ((f + seed * 90) % period) / period;
  if (p > 0.35) return null;
  const jp = p / 0.35;
  const jx = baseX + jp * 260;
  const jy = baseY - Math.sin(jp * Math.PI) * 150;
  const rot = interpolate(jp, [0, 0.5, 1], [-38, 0, 42]);
  return (
    <svg style={{ position: "absolute", left: jx, top: jy, transform: `rotate(${rot}deg)` }} width={110} height={70} viewBox="0 0 110 70">
      <ellipse cx={45} cy={35} rx={38} ry={22} fill="#7FB6D9" />
      <path d="M 78 35 L 106 18 L 106 52 Z" fill="#6AA3C6" />
      <circle cx={24} cy={28} r={5} fill="#1F2833" />
    </svg>
  );
};

const Eagle: React.FC<{ f: number }> = ({ f }) => {
  // Slow figure-eight soar.
  const t = f / 260;
  const x = 960 + Math.sin(t) * 560;
  const y = 330 + Math.sin(t * 2) * 110;
  const bank = Math.cos(t) * 16;
  const flap = Math.max(0, Math.sin(f / 7)) * (Math.sin(f / 90) > 0.7 ? 16 : 3);
  return (
    <svg style={{ position: "absolute", left: x - 110, top: y - 40, transform: `rotate(${bank}deg)` }}
      width={220} height={90} viewBox="0 0 220 90">
      <path d={`M 110 48 Q 60 ${26 - flap} 6 ${40 - flap}`} stroke="#4A3826" strokeWidth={13} fill="none" strokeLinecap="round" />
      <path d={`M 110 48 Q 160 ${26 - flap} 214 ${40 - flap}`} stroke="#4A3826" strokeWidth={13} fill="none" strokeLinecap="round" />
      <ellipse cx={110} cy={50} rx={26} ry={13} fill="#5C4630" />
      <circle cx={132} cy={46} r={8} fill="#E8E4DC" />
      <path d="M 138 44 L 150 47 L 138 50 Z" fill="#E8B44A" />
    </svg>
  );
};

const Whale: React.FC<{ f: number }> = ({ f }) => {
  // Surfacing arc across the chapter; spout at apex.
  const t = (f % 620) / 620;
  const x = -450 + t * (WIDTH + 900);
  const y = 700 - Math.sin(t * Math.PI) * 190;
  const spout = t > 0.42 && t < 0.6;
  const sp = spout ? (t - 0.42) / 0.18 : 0;
  return (
    <div style={{ position: "absolute", left: x, top: y }}>
      <svg width={560} height={260} viewBox="0 0 560 260">
        <path d="M 40 150 Q 120 60 300 70 Q 470 80 520 150 Q 460 200 280 198 Q 110 196 40 150 Z" fill="#41566E" />
        <path d="M 500 140 Q 556 108 548 70 Q 520 96 496 108 Q 520 124 500 140 Z" fill="#38495E" />
        <path d="M 60 150 Q 150 180 300 178" stroke="#5A7188" strokeWidth={7} fill="none" opacity={0.6} />
        <circle cx={120} cy={120} r={10} fill="#111C28" />
        <path d="M 70 160 Q 110 176 160 172" stroke="#2E3F52" strokeWidth={6} fill="none" strokeLinecap="round" />
        {spout && (
          <g opacity={1 - sp}>
            {[-1, 0, 1].map((d) => (
              <path key={d} d={`M 210 70 Q ${210 + d * 34} ${70 - 60 - sp * 60} ${210 + d * 58} ${70 - 90 - sp * 70}`}
                stroke="#DFF1FA" strokeWidth={9} fill="none" strokeLinecap="round" />
            ))}
          </g>
        )}
      </svg>
    </div>
  );
};

const Owl: React.FC<{ x: number; y: number; f: number }> = ({ x, y, f }) => {
  const b = (f % 140) < 8 ? 0.1 : 1;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={120} height={140} viewBox="0 0 120 140">
      <ellipse cx={60} cy={80} rx={40} ry={48} fill="#4E4437" />
      <ellipse cx={60} cy={92} rx={26} ry={30} fill="#6B5D4A" />
      <g transform={`scale(1 ${b})`} style={{ transformOrigin: "60px 58px" } as React.CSSProperties}>
        <circle cx={44} cy={58} r={15} fill="#F2E9C9" /><circle cx={44} cy={58} r={7} fill="#1E1508" />
        <circle cx={76} cy={58} r={15} fill="#F2E9C9" /><circle cx={76} cy={58} r={7} fill="#1E1508" />
      </g>
      <path d="M 55 70 L 60 80 L 65 70 Z" fill="#E8B44A" />
      <path d="M 30 38 L 42 50 M 90 38 L 78 50" stroke="#4E4437" strokeWidth={10} strokeLinecap="round" />
    </svg>
  );
};

// ── Terrain helpers ─────────────────────────────────────────────────────────

const Hills: React.FC<{ y: number; color: string; amp?: number; seed?: number }> = ({ y, color, amp = 70, seed = 1 }) => (
  <svg style={{ position: "absolute", left: -200, top: y }} width={WIDTH + 1400} height={HEIGHT - y + 200}
    viewBox={`0 0 ${WIDTH + 1400} ${HEIGHT - y + 200}`} preserveAspectRatio="none">
    <path d={`M 0 ${amp + 40}
      Q ${400 + seed * 60} ${20} ${800} ${amp + 20} T ${1700} ${amp}
      T ${WIDTH + 1400} ${amp + 30} L ${WIDTH + 1400} ${HEIGHT} L 0 ${HEIGHT} Z`} fill={color} />
  </svg>
);

const Acacia: React.FC<{ x: number; y: number; scale: number; dark: string }> = ({ x, y, scale, dark }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${scale})` }} width={300} height={260} viewBox="0 0 300 260">
    <path d="M 150 250 L 143 150 Q 100 130 70 90 M 143 170 Q 190 140 224 96 M 146 190 Q 120 170 96 160"
      stroke={dark} strokeWidth={12} fill="none" strokeLinecap="round" />
    <ellipse cx={148} cy={78} rx={128} ry={38} fill={dark} />
    <ellipse cx={90} cy={100} rx={60} ry={22} fill={dark} />
    <ellipse cx={215} cy={102} rx={58} ry={20} fill={dark} />
  </svg>
);

const Pine: React.FC<{ x: number; y: number; scale: number; color: string }> = ({ x, y, scale, color }) => (
  <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${scale})` }} width={160} height={300} viewBox="0 0 160 300">
    <rect x={70} y={220} width={20} height={70} fill="#6B4A2A" />
    {[0, 1, 2, 3].map((i) => (
      <path key={i} d={`M 80 ${20 + i * 55} L ${20 + i * 8} ${95 + i * 55} L ${140 - i * 8} ${95 + i * 55} Z`} fill={color} />
    ))}
  </svg>
);

const Grass: React.FC<{ y: number; color: string; f: number; n?: number; seed?: number }> = ({ y, color, f, n = 40, seed = 3 }) => (
  <svg style={{ position: "absolute", left: -100, top: y }} width={WIDTH + 800} height={160} viewBox={`0 0 ${WIDTH + 800} 160`}>
    {Array.from({ length: n }, (_, i) => {
      const gx = (i / n) * (WIDTH + 800) + random(`g${seed}-${i}`) * 40;
      const h = 60 + random(`h${seed}-${i}`) * 70;
      const sway = Math.sin(f / 30 + i * 1.3) * 9;
      return (
        <path key={i} d={`M ${gx} 160 Q ${gx + sway} ${160 - h / 2} ${gx + sway * 1.8} ${160 - h}`}
          stroke={color} strokeWidth={7} fill="none" strokeLinecap="round" />
      );
    })}
  </svg>
);

const Particles: React.FC<{ f: number; n: number; color: string; seed: string; size?: number; drift?: number; glow?: boolean; area?: [number, number, number, number] }> = ({
  f, n, color, seed, size = 5, drift = 16, glow = false, area = [0, 0, WIDTH, HEIGHT],
}) => (
  <AbsoluteFill>
    {Array.from({ length: n }, (_, i) => {
      const px = area[0] + random(`${seed}x${i}`) * area[2] + Math.sin(f / 40 + i * 2.2) * drift * 2;
      const py = area[1] + ((random(`${seed}y${i}`) * area[3] + f * (0.15 + random(`${seed}s${i}`) * 0.5)) % area[3]);
      const tw = 0.35 + 0.65 * Math.abs(Math.sin(f / 22 + i * 3.1));
      return (
        <div key={i} style={{
          position: "absolute", left: px, top: py, width: size, height: size, borderRadius: "50%",
          background: color, opacity: tw,
          boxShadow: glow ? `0 0 ${size * 3}px ${size}px ${color}66` : undefined,
        }} />
      );
    })}
  </AbsoluteFill>
);

const Water: React.FC<{ y: number; base: string; deep: string; f: number; sparkle?: string }> = ({ y, base, deep, f, sparkle = "#EAF8FF" }) => {
  const w1 = Math.sin(f / 10) * 12;
  const w2 = Math.sin(f / 8 + 2) * 9;
  return (
    <svg style={{ position: "absolute", left: -200, top: y }} width={WIDTH + 1400} height={HEIGHT - y + 100}
      viewBox={`0 0 ${WIDTH + 1400} ${HEIGHT - y + 100}`} preserveAspectRatio="none">
      <path d={`M 0 ${40 + w1} Q 400 ${10 + w2} 800 ${36 + w1} T 1650 ${34 + w2} T ${WIDTH + 1400} ${38 + w1} L ${WIDTH + 1400} ${HEIGHT} L 0 ${HEIGHT} Z`} fill={base} />
      <path d={`M 0 ${120 + w2} Q 460 ${86 + w1} 940 ${116 + w2} T ${WIDTH + 1400} ${112 + w1} L ${WIDTH + 1400} ${HEIGHT} L 0 ${HEIGHT} Z`} fill={deep} opacity={0.85} />
      {Array.from({ length: 14 }, (_, i) => (
        <ellipse key={i} cx={140 + i * 240 + Math.sin(f / 18 + i) * 26} cy={60 + (i % 3) * 46 + Math.sin(f / 12 + i * 2) * 8}
          rx={34} ry={4} fill={sparkle} opacity={0.28 + 0.22 * Math.sin(f / 9 + i * 1.7)} />
      ))}
    </svg>
  );
};

// ── Chapters ────────────────────────────────────────────────────────────────

const Ch1Savanna: React.FC<{ lf: number; cam: number }> = ({ lf, cam }) => {
  const dawn = interpolate(lf, [0, 500], [0, 1], clamp);
  return (
    <>
      <Sky top={mix("#2A2547", "#7FB2E5", dawn)} mid={mix("#7A4A5E", "#F5C97B", dawn)} bot={mix("#C96F4A", "#FCE3AE", dawn)} />
      <SunGlow x={1350 - dawn * 120} y={interpolate(dawn, [0, 1], [760, 360])} r={95}
        color={mix("#FF9E4F", "#FFD97A", dawn)} />
      <Cloudbank y={150} scale={1.2} speed={0.5} seed={2} f={lf} tint={mix("#8A6A80", "#FFF6E6", dawn)} op={0.75} />
      <Layer depth={0.1} cam={cam} blur={2.5}>
        <Hills y={560} color={mix("#3A3050", "#C9924E", dawn)} seed={2} />
      </Layer>
      <Layer depth={0.35} cam={cam} blur={1}>
        <Hills y={660} color={mix("#4A3A52", "#B67F3E", dawn)} amp={50} seed={5} />
        <Acacia x={260} y={470} scale={1.1} dark={mix("#241D33", "#6B4A26", dawn)} />
        <Acacia x={1560} y={500} scale={0.85} dark={mix("#241D33", "#6B4A26", dawn)} />
      </Layer>
      <Birds f={lf} y={230} speed={2.2} seed={4} />
      <Layer depth={0.7} cam={cam}>
        <Hills y={780} color={mix("#55405A", "#A87038", dawn)} amp={40} seed={9} />
        <Giraffe x={520 + lf * 0.35} y={430} f={lf} />
        <Elephant x={1050 + lf * 0.3} y={560} f={lf} />
      </Layer>
      <Layer depth={1} cam={cam} blur={2}>
        <Grass y={HEIGHT - 150} color={mix("#3A2E48", "#8A6A2E", dawn)} f={lf} seed={7} />
      </Layer>
      <Particles f={lf} n={14} color="#FFE9B8" seed="dust" size={4} area={[0, 500, WIDTH, 500]} />
      <Grade tint={mix("#31264F", "#FFB55A", dawn)} />
    </>
  );
};

const Ch2Forest: React.FC<{ lf: number; cam: number }> = ({ lf, cam }) => (
  <>
    <Sky top="#9CC29A" mid="#C9E0B8" bot="#E8F0D5" />
    <Layer depth={0.08} cam={cam} blur={3}>
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <rect key={i} x={0} style={{ position: "absolute", left: 120 + i * 360, top: -50 }}
          width={0} height={0} />
      ))}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <div key={i} style={{ position: "absolute", left: 100 + i * 350, top: -60, width: 95, height: HEIGHT + 120,
          background: "#7A9468", borderRadius: 40 }} />
      ))}
    </Layer>
    <Layer depth={0.3} cam={cam} blur={1}>
      {[0, 1, 2, 3].map((i) => (
        <div key={i} style={{ position: "absolute", left: 240 + i * 520, top: -60, width: 130, height: HEIGHT + 120,
          background: "#5E7A4E", borderRadius: 46 }} />
      ))}
    </Layer>
    <Shafts f={lf} color="#FFF7D6" />
    <Layer depth={0.65} cam={cam}>
      <div style={{ position: "absolute", left: 0, top: HEIGHT - 260, width: WIDTH + 800, height: 260, background: "#4E6B3E" }} />
      <Deer x={640 + lf * 0.5} y={620} f={lf} />
      <Deer x={1180 + lf * 0.42} y={700} f={lf + 40} scale={0.8} />
    </Layer>
    <Particles f={lf} n={22} color="#F7EFC9" seed="leaf" size={6} drift={30} area={[0, 0, WIDTH, HEIGHT - 200]} />
    <Layer depth={1} cam={cam} blur={2.5}>
      <div style={{ position: "absolute", left: 1500, top: -80, width: 210, height: HEIGHT + 160, background: "#3E5732", borderRadius: 60 }} />
      <div style={{ position: "absolute", left: -60, top: -80, width: 190, height: HEIGHT + 160, background: "#3E5732", borderRadius: 60 }} />
    </Layer>
    <Grade tint="#5E8A4A" />
  </>
);

const Ch3River: React.FC<{ lf: number; cam: number }> = ({ lf, cam }) => (
  <>
    <Sky top="#8FC8E8" mid="#C2E2EE" bot="#E6F4EA" />
    <Cloudbank y={90} scale={1} speed={0.7} seed={6} f={lf} />
    <Layer depth={0.1} cam={cam} blur={2.5}>
      <Hills y={420} color="#7FA86A" seed={3} />
    </Layer>
    <Layer depth={0.3} cam={cam} blur={1}>
      <Hills y={520} color="#5E8A4E" amp={55} seed={8} />
      <Pine x={220} y={300} scale={0.9} color="#4A7040" />
      <Pine x={1620} y={330} scale={0.75} color="#4A7040" />
    </Layer>
    <Water y={640} base="#5FB0D9" deep="#3E8FBE" f={lf} />
    <Layer depth={0.75} cam={cam}>
      <Heron x={320 + cam * 60} y={520} f={lf} />
    </Layer>
    <Fish2 f={lf} seed={0} baseX={780} baseY={700} />
    <Fish2 f={lf} seed={2} baseX={1240} baseY={730} />
    <Particles f={lf} n={8} color="#FFFFFF" seed="mist" size={26} drift={10} area={[0, 560, WIDTH, 200]} />
    <Grade tint="#5FA8C9" strength={0.1} />
  </>
);

const Ch4Mountain: React.FC<{ lf: number; cam: number }> = ({ lf, cam }) => (
  <>
    <Sky top="#6FA8DC" mid="#A8CBE8" bot="#E2EDF5" />
    <SunGlow x={330} y={240} r={70} color="#FFF3D0" halo={2.6} />
    <Layer depth={0.08} cam={cam} blur={2}>
      <svg style={{ position: "absolute", left: -200, top: 260 }} width={WIDTH + 1400} height={820} viewBox={`0 0 ${WIDTH + 1400} 820`} preserveAspectRatio="none">
        <path d={`M 0 820 L 340 260 L 560 470 L 860 120 L 1160 480 L 1450 220 L 1750 520 L 2100 300 L ${WIDTH + 1400} 820 Z`} fill="#8FA6C4" />
        <path d="M 860 120 L 780 260 L 940 260 Z M 1450 220 L 1385 340 L 1516 340 Z M 340 260 L 285 370 L 396 370 Z" fill="#F2F7FC" />
      </svg>
    </Layer>
    <Cloudbank y={430} scale={1.5} speed={0.9} seed={11} f={lf} op={0.85} />
    <Layer depth={0.35} cam={cam} blur={0.5}>
      <svg style={{ position: "absolute", left: -200, top: 480 }} width={WIDTH + 1400} height={620} viewBox={`0 0 ${WIDTH + 1400} 620`} preserveAspectRatio="none">
        <path d={`M 0 620 L 420 120 L 760 400 L 1120 60 L 1520 420 L 1900 160 L ${WIDTH + 1400} 620 Z`} fill="#5E7898" />
        <path d="M 1120 60 L 1042 210 L 1198 210 Z M 420 120 L 356 250 L 484 250 Z" fill="#EAF2F8" />
      </svg>
    </Layer>
    <Eagle f={lf} />
    <Layer depth={0.8} cam={cam}>
      <svg style={{ position: "absolute", left: -200, top: 700 }} width={WIDTH + 1400} height={420} viewBox={`0 0 ${WIDTH + 1400} 420`} preserveAspectRatio="none">
        <path d={`M 0 420 L 500 60 L 980 380 L 1480 40 L ${WIDTH + 1400} 420 Z`} fill="#3E5570" />
      </svg>
      <Pine x={420} y={780} scale={0.8} color="#2E4A3A" />
      <Pine x={1360} y={800} scale={0.68} color="#2E4A3A" />
    </Layer>
    <Particles f={lf} n={26} color="#FFFFFF" seed="snow" size={5} drift={22} />
    <Grade tint="#5E78A8" strength={0.12} />
  </>
);

const Ch5Ocean: React.FC<{ lf: number; cam: number }> = ({ lf, cam }) => (
  <>
    <Sky top="#7FB8DC" mid="#BFE0EA" bot="#EAF6F2" />
    <SunGlow x={1560} y={210} r={80} color="#FFF0C4" halo={2.8} />
    <Cloudbank y={120} scale={1.3} speed={0.8} seed={14} f={lf} />
    <Birds f={lf} y={180} speed={1.8} seed={9} color="#5A6B78" count={4} />
    <Layer depth={0.15} cam={cam} blur={1.5} pan={260}>
      <Water y={470} base="#4E9CC9" deep="#2E7AA8" f={lf * 0.8} />
    </Layer>
    <Whale f={lf} />
    <Layer depth={0.7} cam={cam} pan={260}>
      <Water y={760} base="#3E8FBE" deep="#25628C" f={lf} />
    </Layer>
    <Particles f={lf} n={10} color="#EAF8FF" seed="spray" size={7} drift={14} area={[0, 500, WIDTH, 400]} />
    <Grade tint="#3E7AA8" strength={0.12} />
  </>
);

const Ch6Night: React.FC<{ lf: number; cam: number; globalFrame: number }> = ({ lf, cam, globalFrame }) => {
  const credits = lf > 660;
  const ca = interpolate(lf, [660, 720], [0, 1], clamp);
  return (
    <>
      <Sky top="#0C1030" mid="#1B2248" bot="#2A3358" />
      {Array.from({ length: 70 }, (_, i) => {
        const tw = 0.25 + 0.75 * Math.abs(Math.sin(lf / 14 + i * 2.7));
        return (
          <div key={i} style={{
            position: "absolute", left: random(`stx${i}`) * WIDTH, top: random(`sty${i}`) * 620,
            width: 2 + random(`sts${i}`) * 3, height: 2 + random(`sts${i}`) * 3,
            borderRadius: "50%", background: "#EAF0FF", opacity: tw,
          }} />
        );
      })}
      <SunGlow x={1490} y={220} r={64} color="#F3EEDD" halo={2.4} />
      <Layer depth={0.15} cam={cam} blur={2}>
        <Hills y={600} color="#141A38" seed={4} />
      </Layer>
      <Layer depth={0.4} cam={cam} blur={0.5}>
        <Hills y={700} color="#0E1428" amp={55} seed={12} />
        <Pine x={300} y={520} scale={1} color="#0B1020" />
        <Pine x={1520} y={540} scale={0.9} color="#0B1020" />
      </Layer>
      <Layer depth={0.75} cam={cam}>
        <div style={{ position: "absolute", left: 0, top: HEIGHT - 220, width: WIDTH + 800, height: 220, background: "#080C1C" }} />
        <Owl x={430} y={560} f={lf} />
      </Layer>
      <Particles f={lf} n={26} color="#D9F27A" seed="fly" size={6} drift={34} glow area={[0, 420, WIDTH, 520]} />
      <Grade tint="#1B2248" strength={0.2} />
      {credits && (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: ca }}>
          <div style={{ textAlign: "center", fontFamily: "'Liberation Sans', Arial, sans-serif" }}>
            <div style={{ fontSize: 150, fontWeight: 800, color: "#F2EEDF", letterSpacing: 30,
              textShadow: "0 6px 30px rgba(0,0,0,0.6)" }}>WILD</div>
            <div style={{ fontSize: 34, fontWeight: 700, color: "#C9CFE8", marginTop: 22, letterSpacing: 4 }}>
              a ViralReel Studio platform film
            </div>
            <div style={{ fontSize: 24, color: "#8A93B8", marginTop: 16 }}>
              six continuous shots · eighteen chained segments · one take each
            </div>
          </div>
        </AbsoluteFill>
      )}
    </>
  );
};

// Opening title over chapter 1.
const OpeningTitle: React.FC<{ lf: number }> = ({ lf }) => {
  if (lf > 200) return null;
  const a = interpolate(lf, [20, 60, 150, 200], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: a }}>
      <div style={{ textAlign: "center", fontFamily: "'Liberation Sans', Arial, sans-serif" }}>
        <div style={{ fontSize: 170, fontWeight: 800, color: "#FFF6E0", letterSpacing: 36,
          textShadow: "0 8px 40px rgba(30,10,0,0.55)" }}>WILD</div>
        <div style={{ fontSize: 30, fontWeight: 700, color: "#FFE9BC", letterSpacing: 10, marginTop: 14 }}>
          A NATURE DOCUMENTARY
        </div>
      </div>
    </AbsoluteFill>
  );
};

const CHAPTER_TITLES = ["Dawn on the Savanna", "The Old Forest", "The River Road",
  "Thin Air", "The Blue Wilderness", "Night Shift"];

export const Wild: React.FC = () => {
  const { f, c, lf, cam } = useChapter();
  return (
    <AbsoluteFill style={{ background: "#05060A" }}>
      {c === 0 && <Ch1Savanna lf={lf} cam={cam} />}
      {c === 1 && <Ch2Forest lf={lf} cam={cam} />}
      {c === 2 && <Ch3River lf={lf} cam={cam} />}
      {c === 3 && <Ch4Mountain lf={lf} cam={cam} />}
      {c === 4 && <Ch5Ocean lf={lf} cam={cam} />}
      {c === 5 && <Ch6Night lf={lf} cam={cam} globalFrame={f} />}
      {c === 0 && <OpeningTitle lf={lf} />}
      <DocChrome chapter={c} title={CHAPTER_TITLES[c]} lf={lf} />
    </AbsoluteFill>
  );
};
