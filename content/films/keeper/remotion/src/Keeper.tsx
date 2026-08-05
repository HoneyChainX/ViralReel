import React from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";

// THE KEEPER — Acts 1-2 (2.5D lane). Act 3 is true-3D (bpy/Cycles).
// 24fps to match the 3D act. Each act is ONE continuous camera move → chain-safe.
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const FPS = 24;
export const ACT = 528; // 22s per act
export const DURATION_IN_FRAMES = 2 * ACT; // acts 1-2 only; act 3 renders in Cycles

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const mix = (a: string, b: string, t: number): string => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const u = Math.min(1, Math.max(0, t));
  return `rgb(${pa.map((v, i) => Math.round(v + (pb[i] - v) * u)).join(",")})`;
};

// ── KIP_001 — the casting sheet, executed. Canon: mustard oilskin w/ three dark
// toggles, navy knit cap pulled low, white squared beard, black sea boots.
const KIP = {
  coat: "#D9A24E", trouser: "#3A3F4A", boot: "#16181D", cap: "#2A3358",
  skin: "#C98B6B", beard: "#F2EFE8", nose: "#D98A7E",
};

const Kip: React.FC<{ x: number; y: number; f: number; scale?: number; mode: "walk" | "row"; flip?: boolean }> = ({
  x, y, f, scale = 1, mode, flip,
}) => {
  const step = mode === "walk" ? Math.sin(f / 6) * 10 : 0;
  const sway = Math.sin(f / (mode === "walk" ? 6 : 14)) * (mode === "walk" ? 2.5 : 4);
  const rowArm = mode === "row" ? Math.sin(f / 14) * 26 : 0;
  return (
    <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${flip ? -scale : scale}, ${scale})` }}
      width={220} height={300} viewBox="0 0 220 300">
      <g transform={`rotate(${sway} 110 190)`}>
        {mode === "walk" && (
          <g stroke={KIP.boot} strokeWidth={20} strokeLinecap="round">
            <line x1={95} y1={230} x2={95 - step} y2={288} />
            <line x1={125} y1={230} x2={125 + step} y2={288} />
          </g>
        )}
        {/* coat — canon mustard oilskin, high collar */}
        <path d={`M 70 130 Q 68 100 92 92 L 128 92 Q 152 100 150 130 L 156 ${232 + (mode === "row" ? 10 : 0)} L 64 ${232 + (mode === "row" ? 10 : 0)} Z`} fill={KIP.coat} />
        <path d="M 86 96 L 134 96 L 130 82 L 90 82 Z" fill={KIP.coat} />
        {[142, 168, 194].map((cy) => <circle key={cy} cx={110} cy={cy} r={5.5} fill="#4A3A1E" />)}
        {/* rowing arms */}
        {mode === "row" && (
          <g stroke={KIP.coat} strokeWidth={18} strokeLinecap="round">
            <line x1={88} y1={140} x2={54 - rowArm * 0.5} y2={188 + rowArm * 0.3} />
            <line x1={132} y1={140} x2={166 + rowArm * 0.5} y2={188 + rowArm * 0.3} />
          </g>
        )}
        {/* head: cap pulled low, wide dot eyes, squared white beard */}
        <g transform={`translate(110 ${64 + (mode === "walk" ? Math.abs(step) * 0.3 : Math.sin(f / 14) * 2)})`}>
          <circle r={30} fill={KIP.skin} />
          <path d="M -30 -6 Q -30 -34 0 -34 Q 30 -34 30 -6 L 30 -1 L -30 -1 Z" fill={KIP.cap} />
          <rect x={-32} y={-4} width={64} height={7} rx={3.5} fill={KIP.cap} />
          <circle cx={-13} cy={7} r={3.4} fill="#1E1A14" />
          <circle cx={13} cy={7} r={3.4} fill="#1E1A14" />
          <path d="M -11 1 Q -13 -2 -18 -1 M 11 1 Q 13 -2 18 -1" stroke={KIP.beard} strokeWidth={4} fill="none" strokeLinecap="round" />
          <circle cx={0} cy={13} r={5.5} fill={KIP.nose} />
          <path d="M -18 16 L 18 16 L 15 40 L -15 40 Z" fill={KIP.beard} />
        </g>
      </g>
    </svg>
  );
};

const Layer: React.FC<{ depth: number; cam: number; children: React.ReactNode; blur?: number; pan?: number }> = ({
  depth, cam, children, blur, pan = 560,
}) => (
  <AbsoluteFill style={{
    transform: `translateX(${-cam * pan * (0.2 + depth)}px)`,
    filter: blur ? `blur(${blur}px)` : undefined,
  }}>
    {children}
  </AbsoluteFill>
);

const Sky: React.FC<{ top: string; mid: string; bot: string }> = ({ top, mid, bot }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, ${top} 0%, ${mid} 55%, ${bot} 100%)` }} />
);

const Gulls: React.FC<{ f: number; y: number; seed: number; color?: string }> = ({ f, y, seed, color = "#3A3F4A" }) => {
  const x = ((seed * 617 + f * 1.7) % (WIDTH + 600)) - 400;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={260} height={90} viewBox="0 0 260 90">
      {[0, 1, 2].map((i) => {
        const w = Math.sin(f / 5 + i * 1.4) * 10;
        const bx = i * 85; const by = (i % 2) * 26 + Math.sin(f / 15 + i) * 5;
        return <path key={i} d={`M ${bx} ${by + 24} Q ${bx + 17} ${by + 24 - w} ${bx + 34} ${by + 24}
                                 M ${bx + 34} ${by + 24} Q ${bx + 51} ${by + 24 - w} ${bx + 68} ${by + 24}`}
          stroke={color} strokeWidth={5} fill="none" strokeLinecap="round" />;
      })}
    </svg>
  );
};

const Sea: React.FC<{ y: number; base: string; deep: string; f: number; glint: string }> = ({ y, base, deep, f, glint }) => {
  const w1 = Math.sin(f / 11) * 10; const w2 = Math.sin(f / 8 + 2) * 8;
  return (
    <svg style={{ position: "absolute", left: -300, top: y }} width={WIDTH + 1800} height={HEIGHT - y + 120}
      viewBox={`0 0 ${WIDTH + 1800} ${HEIGHT - y + 120}`} preserveAspectRatio="none">
      <path d={`M 0 ${44 + w1} Q 480 ${12 + w2} 960 ${40 + w1} T 1980 ${38 + w2} T ${WIDTH + 1800} ${42 + w1} L ${WIDTH + 1800} 900 L 0 900 Z`} fill={base} />
      <path d={`M 0 ${140 + w2} Q 540 ${102 + w1} 1100 ${134 + w2} T ${WIDTH + 1800} ${130 + w1} L ${WIDTH + 1800} 900 L 0 900 Z`} fill={deep} opacity={0.85} />
      {Array.from({ length: 16 }, (_, i) => (
        <ellipse key={i} cx={160 + i * 240 + Math.sin(f / 16 + i) * 30} cy={70 + (i % 4) * 44 + Math.sin(f / 10 + i * 2) * 7}
          rx={38} ry={4} fill={glint} opacity={0.25 + 0.2 * Math.sin(f / 8 + i * 1.7)} />
      ))}
    </svg>
  );
};

// ── ACT 1: the walk — cottage door, cliff path, gold evening (one lateral track)
const Act1: React.FC<{ lf: number }> = ({ lf }) => {
  const t = lf / ACT;
  const cam = interpolate(t, [0, 1], [0, 1], { easing: Easing.inOut(Easing.sin) });
  const dusk = t;
  return (
    <>
      <Sky top={mix("#8FB8DC", "#6E88B8", dusk)} mid={mix("#F2CE8E", "#D9976E", dusk)} bot={mix("#F7E3B8", "#E0AC80", dusk)} />
      <div style={{ position: "absolute", left: 300 - cam * 140, top: 170, width: 150, height: 150, borderRadius: "50%",
        background: "radial-gradient(circle, #FFF3D0 0%, #FFD98E 55%, transparent 72%)" }} />
      <Gulls f={lf} y={200} seed={3} />
      <Layer depth={0.08} cam={cam} blur={2.5}>
        <Sea y={640} base={mix("#5F9CC4", "#4A7FA8", dusk)} deep={mix("#3E7096", "#2E5578", dusk)} f={lf} glint="#FFE9B8" />
      </Layer>
      <Layer depth={0.35} cam={cam} blur={0.8}>
        {/* headland with distant lighthouse — the destination, seen from home */}
        <svg style={{ position: "absolute", left: 1500, top: 380 }} width={700} height={420} viewBox="0 0 700 420">
          <path d="M 0 420 L 120 210 Q 300 130 480 190 L 700 420 Z" fill={mix("#7A8CA0", "#5C6E86", dusk)} />
          <g transform="translate(360 60)">
            <path d="M -16 130 L -10 30 L 10 30 L 16 130 Z" fill="#E8E2D4" />
            <rect x={-13} y={52} width={26} height={16} fill="#A84838" />
            <rect x={-13} y={92} width={26} height={16} fill="#A84838" />
            <rect x={-11} y={16} width={22} height={16} rx={3} fill="#2A3040" />
            <path d="M -13 16 L 0 2 L 13 16 Z" fill="#A84838" />
          </g>
        </svg>
      </Layer>
      <Layer depth={0.7} cam={cam}>
        {/* cliff path */}
        <svg style={{ position: "absolute", left: -200, top: 700 }} width={WIDTH + 1600} height={420}
          viewBox={`0 0 ${WIDTH + 1600} 420`} preserveAspectRatio="none">
          <path d={`M 0 90 Q 800 40 1700 80 T ${WIDTH + 1600} 70 L ${WIDTH + 1600} 420 L 0 420 Z`}
            fill={mix("#8A9A6E", "#6E7E58", dusk)} />
          <path d={`M 0 130 Q 800 84 1700 122 T ${WIDTH + 1600} 112`} stroke={mix("#C9B98E", "#A8986E", dusk)}
            strokeWidth={26} fill="none" />
        </svg>
        {/* cottage at start, door ajar, chimney smoke */}
        <svg style={{ position: "absolute", left: 60, top: 470 }} width={420} height={330} viewBox="0 0 420 330">
          <rect x={40} y={130} width={300} height={170} rx={8} fill="#E8E2D4" />
          <path d="M 20 140 L 190 40 L 360 140 Z" fill="#A84838" />
          <rect x={250} y={60} width={30} height={60} fill="#8A8478" />
          <rect x={90} y={190} width={70} height={110} rx={4} fill="#4A3A28" />
          <rect x={200} y={190} width={80} height={64} rx={4} fill={mix("#FFE9A8", "#FFD98E", 0.5)} stroke="#4A3A28" strokeWidth={8} />
          {[0, 1, 2].map((i) => (
            <ellipse key={i} cx={265 + Math.sin(lf / 20 + i * 2) * 10 + i * 6} cy={40 - i * 24} rx={12 + i * 5} ry={8 + i * 3}
              fill="#DDD8CC" opacity={0.5 - i * 0.13} />
          ))}
        </svg>
        {/* KIP walks the path — the continuous move of the act */}
        <Kip x={330 + t * 1450} y={620} f={lf} mode="walk" />
      </Layer>
      <Layer depth={1} cam={cam} blur={2}>
        <svg style={{ position: "absolute", left: -100, top: HEIGHT - 130 }} width={WIDTH + 900} height={140}
          viewBox={`0 0 ${WIDTH + 900} 140`}>
          {Array.from({ length: 34 }, (_, i) => {
            const gx = (i / 34) * (WIDTH + 900) + random(`g${i}`) * 40;
            const sway = Math.sin(lf / 24 + i * 1.3) * 8;
            return <path key={i} d={`M ${gx} 140 Q ${gx + sway} 90 ${gx + sway * 1.7} ${50 + random(`h${i}`) * 40}`}
              stroke={mix("#6E8850", "#55663E", dusk)} strokeWidth={6} fill="none" strokeLinecap="round" />;
          })}
        </svg>
      </Layer>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, transparent 58%, rgba(20,14,30,0.30) 100%)" }} />
    </>
  );
};

// ── ACT 2: the crossing — rowboat, open water, sun letting go (one slow push)
const Act2: React.FC<{ lf: number }> = ({ lf }) => {
  const t = lf / ACT;
  const cam = interpolate(t, [0, 1], [0, 1], { easing: Easing.inOut(Easing.sin) });
  const dusk = t;
  const bob = Math.sin(lf / 14) * 9;
  const boatX = 300 + t * 520;
  return (
    <>
      <Sky top={mix("#6E88B8", "#42507E", dusk)} mid={mix("#D9976E", "#8E5E7E", dusk)} bot={mix("#E0AC80", "#5E4A6E", dusk)} />
      <div style={{ position: "absolute", left: 1280, top: interpolate(dusk, [0, 1], [430, 610]), width: 190, height: 190,
        borderRadius: "50%", background: `radial-gradient(circle, ${mix("#FFE9B8", "#FF9E5E", dusk)} 0%, ${mix("#FFD98E", "#E8784A", dusk)} 55%, transparent 74%)`,
        opacity: interpolate(dusk, [0, 0.85, 1], [1, 0.9, 0.4]) }} />
      <Gulls f={lf} y={170} seed={8} color={mix("#3A3F4A", "#2A2F3A", dusk)} />
      {/* sun road on the water */}
      <div style={{ position: "absolute", left: 1300, top: 640, width: 150, height: 330,
        background: `linear-gradient(180deg, ${mix("#FFE9B8", "#E8784A", dusk)}66 0%, transparent 90%)`,
        transform: "perspective(300px) rotateX(55deg)", filter: "blur(6px)" }} />
      <Layer depth={0.1} cam={cam} blur={2} pan={240}>
        <Sea y={600} base={mix("#4A7FA8", "#35507A", dusk)} deep={mix("#2E5578", "#22375A", dusk)} f={lf * 0.8} glint={mix("#FFE9B8", "#FFB98E", dusk)} />
      </Layer>
      {/* destination island grows — the push of the act */}
      <Layer depth={0.3} cam={cam} blur={0.5} pan={240}>
        <svg style={{ position: "absolute", left: 1450 - t * 240, top: 420 - t * 60, transform: `scale(${0.8 + t * 0.55})`, transformOrigin: "left top" }}
          width={520} height={400} viewBox="0 0 520 400">
          <path d="M 20 400 Q 120 260 260 250 Q 400 258 500 400 Z" fill={mix("#5C6E86", "#3E4A66", dusk)} />
          <g transform="translate(250 110)">
            <path d="M -22 150 L -14 20 L 14 20 L 22 150 Z" fill="#E8E2D4" />
            <rect x={-18} y={46} width={36} height={22} fill="#A84838" />
            <rect x={-18} y={100} width={36} height={22} fill="#A84838" />
            <rect x={-15} y={0} width={30} height={22} rx={4} fill="#2A3040" />
            <path d="M -18 0 L 0 -18 L 18 0 Z" fill="#A84838" />
          </g>
        </svg>
      </Layer>
      <Layer depth={0.7} cam={cam} pan={240}>
        {/* the rowboat — KIP rows, wake trails */}
        <svg style={{ position: "absolute", left: boatX, top: 640 + bob }} width={560} height={300} viewBox="0 0 560 300">
          <path d={`M 40 150 Q 60 210 160 216 L 420 216 Q 500 208 528 148 L 470 150 Q 420 186 300 186 L 150 186 Q 90 180 40 150 Z`}
            fill="#6E4A2E" />
          <path d="M 40 150 L 528 148 L 500 168 L 70 170 Z" fill="#8A5E3A" />
          <line x1={330} y1={160} x2={430 + Math.sin(lf / 14) * 40} y2={230 + Math.cos(lf / 14) * 16}
            stroke="#4A3A28" strokeWidth={9} strokeLinecap="round" />
        </svg>
        <Kip x={boatX + 160} y={556 + bob} f={lf} mode="row" scale={0.95} />
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ position: "absolute", left: boatX - 60 - i * 90 + Math.sin(lf / 12 + i) * 8,
            top: 850 + bob * 0.5 + i * 8, width: 110 - i * 24, height: 7, borderRadius: 4,
            background: mix("#EAF4FF", "#B8CCE8", dusk), opacity: 0.4 - i * 0.11 }} />
        ))}
      </Layer>
      <Layer depth={1} cam={cam} blur={2.5} pan={240}>
        <Sea y={860} base={mix("#35507A", "#26385E", dusk)} deep={mix("#22375A", "#182848", dusk)} f={lf} glint="#8EA8CC" />
      </Layer>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 42%, transparent 55%, rgba(10,10,26,0.36) 100%)" }} />
    </>
  );
};

export const Keeper: React.FC = () => {
  const f = useCurrentFrame();
  const act = f < ACT ? 1 : 2;
  const lf = act === 1 ? f : f - ACT;
  return (
    <AbsoluteFill style={{ background: "#0A0C14" }}>
      {act === 1 ? <Act1 lf={lf} /> : <Act2 lf={lf} />}
    </AbsoluteFill>
  );
};
