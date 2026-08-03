import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;
export const DURATION_IN_FRAMES = 60 * FPS;

// Scene boundaries (frames)
const S2 = 180; // desert — Cami intro
const S3 = 480; // discovers the sea
const S4 = 780; // Finn pops up
const S5 = 1020; // beach ball game
const S6 = 1380; // sunset dance
const S7 = 1620; // end card

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ── Backdrop ────────────────────────────────────────────────────────────────

const Sky: React.FC = () => {
  const f = useCurrentFrame();
  // Day sky → warm sunset during S6, holds for the end card.
  const warm = interpolate(f, [S6 - 60, S6 + 120], [0, 1], { ...clamp, easing: Easing.inOut(Easing.ease) });
  const top = warm < 0.5 ? "#8ED4F7" : "#F7A278";
  const topMix = interpolate(warm, [0, 1], [0, 1]);
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg,
          ${mix("#7EC9F5", "#7A5A9E", topMix)} 0%,
          ${mix("#AEE3FA", "#F7A278", topMix)} 55%,
          ${mix("#D8F1FC", "#FFD3A3", topMix)} 100%)`,
      }}
    />
  );
};

const mix = (a: string, b: string, t: number): string => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const pc = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
  return `rgb(${pc[0]},${pc[1]},${pc[2]})`;
};

const Sun: React.FC = () => {
  const f = useCurrentFrame();
  const rot = (f / FPS) * 12; // slow ray spin
  const sunset = interpolate(f, [S6 - 60, S7], [0, 1], { ...clamp, easing: Easing.inOut(Easing.ease) });
  const y = interpolate(sunset, [0, 1], [260, 720]);
  const color = mix("#FFD93D", "#FF9E4F", sunset);
  return (
    <div style={{ position: "absolute", left: 790, top: y, transform: `rotate(${rot}deg)` }}>
      <svg width={340} height={340} viewBox="-170 -170 340 340">
        {Array.from({ length: 12 }, (_, i) => (
          <rect key={i} x={-14} y={-160} width={28} height={70} rx={14} fill={color}
            transform={`rotate(${i * 30})`} opacity={0.9} />
        ))}
        <circle r={92} fill={color} />
        <circle cx={-26} cy={-12} r={9} fill="#7A5210" />
        <circle cx={26} cy={-12} r={9} fill="#7A5210" />
        <path d="M -30 22 Q 0 48 30 22" stroke="#7A5210" strokeWidth={9} fill="none" strokeLinecap="round" />
      </svg>
    </div>
  );
};

const Cloud: React.FC<{ y: number; scale: number; speed: number; offset: number }> = ({ y, scale, speed, offset }) => {
  const f = useCurrentFrame();
  const x = ((offset + f * speed) % (WIDTH + 500)) - 400;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={300 * scale} height={120 * scale} viewBox="0 0 300 120">
      <g fill="#FFFFFF" opacity={0.92}>
        <ellipse cx={80} cy={80} rx={70} ry={38} />
        <ellipse cx={150} cy={60} rx={80} ry={48} />
        <ellipse cx={225} cy={82} rx={65} ry={34} />
      </g>
    </svg>
  );
};

// Desert floor with soft dunes. Slides left as Cami "travels" in S3.
const Desert: React.FC<{ shift: number }> = ({ shift }) => (
  <svg style={{ position: "absolute", left: -shift, bottom: 0 }} width={WIDTH * 2} height={760}
    viewBox={`0 0 ${WIDTH * 2} 760`} preserveAspectRatio="none">
    <path d={`M0 220 Q 300 80 640 210 T 1300 200 T 2160 190 L 2160 760 L 0 760 Z`} fill="#F0C070" />
    <path d={`M0 360 Q 420 240 900 350 T 2160 330 L 2160 760 L 0 760 Z`} fill="#E8AE55" />
    <path d={`M0 520 Q 500 430 1100 510 T 2160 500 L 2160 760 L 0 760 Z`} fill="#DE9C41" />
    {/* little cacti */}
    <g fill="#4E9B4E">
      <rect x={330} y={300} width={26} height={90} rx={13} />
      <rect x={300} y={320} width={20} height={44} rx={10} transform="rotate(-18 310 342)" />
      <rect x={1500} y={260} width={26} height={90} rx={13} />
      <rect x={1552} y={280} width={20} height={44} rx={10} transform="rotate(16 1562 302)" />
    </g>
  </svg>
);

// Sea slides in from the right during S3 and stays.
const Sea: React.FC<{ reveal: number }> = ({ reveal }) => {
  const f = useCurrentFrame();
  const x = interpolate(reveal, [0, 1], [WIDTH, 340]);
  const w1 = Math.sin(f / 9) * 16;
  const w2 = Math.sin(f / 7 + 2) * 12;
  return (
    <div style={{ position: "absolute", left: x, bottom: 0, width: WIDTH, height: 640 }}>
      <svg width={WIDTH} height={640} viewBox={`0 0 ${WIDTH} 640`} preserveAspectRatio="none">
        <path d={`M0 ${120 + w1} Q 180 ${70 + w2} 360 ${115 + w1} T 720 ${112 + w2} T 1080 ${118 + w1} L 1080 640 L 0 640 Z`} fill="#3AA7D9" />
        <path d={`M0 ${190 + w2} Q 200 ${150 + w1} 420 ${185 + w2} T 840 ${182 + w1} T 1080 ${188 + w2} L 1080 640 L 0 640 Z`} fill="#2B8FC2" opacity={0.9} />
        {/* foam */}
        <path d={`M0 ${122 + w1} Q 180 ${72 + w2} 360 ${117 + w1} T 720 ${114 + w2} T 1080 ${120 + w1}`} stroke="#EAF8FF" strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.85} />
      </svg>
    </div>
  );
};

// ── Characters ──────────────────────────────────────────────────────────────

const blink = (f: number, seed: number): number => {
  const t = (f + seed) % 110;
  return t < 6 ? 0.12 : 1; // eye scaleY
};

const Camel: React.FC<{ x: number; y: number; hop: number; scale?: number; flip?: boolean; frame: number }> = ({
  x, y, hop, scale = 1, flip = false, frame,
}) => {
  // hop: 0..1 within a bounce cycle → vertical arc + squash/stretch
  const air = Math.sin(hop * Math.PI);
  const dy = -air * 120;
  const squash = hop < 0.08 || hop > 0.92 ? 0.88 : 1 + air * 0.06;
  const legSwing = Math.sin(hop * Math.PI * 2) * 14;
  return (
    <div style={{
      position: "absolute", left: x, top: y + dy,
      transform: `scale(${flip ? -scale : scale}, ${scale * squash})`, transformOrigin: "bottom center",
    }}>
      <svg width={360} height={330} viewBox="0 0 360 330">
        {/* legs */}
        <g stroke="#B97F41" strokeWidth={26} strokeLinecap="round">
          <line x1={110} y1={230} x2={110 - legSwing} y2={318} />
          <line x1={165} y1={235} x2={165 + legSwing} y2={318} />
          <line x1={225} y1={235} x2={225 - legSwing} y2={318} />
          <line x1={278} y1={230} x2={278 + legSwing} y2={318} />
        </g>
        {/* body + humps */}
        <path d="M 70 240 Q 60 150 130 140 Q 150 92 195 118 Q 240 88 262 132 Q 330 140 318 235 Q 300 268 195 268 Q 90 268 70 240 Z" fill="#D99A56" />
        {/* tail */}
        <path d="M 318 190 Q 352 176 350 148" stroke="#B97F41" strokeWidth={16} fill="none" strokeLinecap="round" />
        <circle cx={352} cy={144} r={13} fill="#8A5A24" />
        {/* neck + head */}
        <path d="M 88 210 Q 40 190 44 120 Q 46 84 70 78" stroke="#D99A56" strokeWidth={52} fill="none" strokeLinecap="round" />
        <g>
          <ellipse cx={62} cy={62} rx={52} ry={42} fill="#D99A56" />
          <ellipse cx={22} cy={74} rx={18} ry={13} fill="#C4854A" />
          {/* eye with blink */}
          <g transform={`translate(70 52) scale(1 ${blink(frame, 0)})`}>
            <circle r={15} fill="#FFFFFF" />
            <circle cx={3} r={8} fill="#3B2A16" />
          </g>
          {/* smile + ear */}
          <path d="M 30 84 Q 42 96 58 90" stroke="#7A4E1E" strokeWidth={7} fill="none" strokeLinecap="round" />
          <ellipse cx={96} cy={34} rx={11} ry={16} fill="#B97F41" transform="rotate(24 96 34)" />
        </g>
      </svg>
    </div>
  );
};

const Fish: React.FC<{ x: number; y: number; pop: number; frame: number; scale?: number }> = ({ x, y, pop, frame, scale = 1 }) => {
  const wiggle = Math.sin(frame / 4) * 14;
  const bob = Math.sin(frame / 11) * 12;
  return (
    <div style={{
      position: "absolute", left: x, top: y + (1 - pop) * 240 + bob,
      transform: `scale(${scale})`, transformOrigin: "center", opacity: pop > 0.02 ? 1 : 0,
    }}>
      <svg width={300} height={220} viewBox="0 0 300 220">
        {/* tail */}
        <path d={`M 232 110 L 296 ${64 + wiggle} L 296 ${156 + wiggle} Z`} fill="#F76B3C" />
        {/* body */}
        <ellipse cx={140} cy={110} rx={110} ry={76} fill="#FF8A5C" />
        <path d="M 92 40 Q 130 6 160 40 Q 128 52 92 40 Z" fill="#F76B3C" />
        {/* stripes */}
        <path d="M 150 40 Q 172 110 150 180" stroke="#FFD1B8" strokeWidth={16} fill="none" strokeLinecap="round" />
        <path d="M 192 52 Q 210 110 192 168" stroke="#FFD1B8" strokeWidth={14} fill="none" strokeLinecap="round" />
        {/* face */}
        <g transform={`translate(78 92) scale(1 ${blink(frame, 37)})`}>
          <circle r={20} fill="#FFFFFF" />
          <circle cx={-4} r={10} fill="#26364A" />
        </g>
        <path d="M 34 128 Q 52 144 74 136" stroke="#B24A22" strokeWidth={8} fill="none" strokeLinecap="round" />
        {/* fin */}
        <path d={`M 140 150 Q ${120 + wiggle / 2} 186 168 178 Q 158 160 140 150 Z`} fill="#F76B3C" />
      </svg>
    </div>
  );
};

const BeachBall: React.FC<{ x: number; y: number; rot: number; squash: number }> = ({ x, y, rot, squash }) => (
  <div style={{ position: "absolute", left: x, top: y, transform: `rotate(${rot}deg) scale(1, ${squash})` }}>
    <svg width={190} height={190} viewBox="-95 -95 190 190">
      <circle r={90} fill="#FFFFFF" />
      <path d="M 0 -90 A 90 90 0 0 1 78 45 L 0 0 Z" fill="#FF5A5F" />
      <path d="M 78 45 A 90 90 0 0 1 -78 45 L 0 0 Z" fill="#3AA7D9" />
      <path d="M -78 45 A 90 90 0 0 1 0 -90 L 0 0 Z" fill="#FFD93D" />
      <circle r={90} fill="none" stroke="#2C3A47" strokeWidth={6} opacity={0.25} />
    </svg>
  </div>
);

const Splash: React.FC<{ t: number; x: number; y: number }> = ({ t, x, y }) => {
  if (t <= 0 || t >= 1) return null;
  return (
    <svg style={{ position: "absolute", left: x, top: y }} width={420} height={300} viewBox="0 0 420 300">
      {Array.from({ length: 9 }, (_, i) => {
        const a = (i / 8) * Math.PI;
        const r = t * 190;
        return (
          <circle key={i} cx={210 + Math.cos(a) * r} cy={250 - Math.sin(a) * r * 1.25}
            r={16 * (1 - t)} fill="#BFE8FF" opacity={1 - t} />
        );
      })}
    </svg>
  );
};

const StarPop: React.FC<{ t: number; x: number; y: number; color?: string }> = ({ t, x, y, color = "#FFD93D" }) => {
  if (t <= 0 || t >= 1) return null;
  const s = Math.sin(t * Math.PI);
  return (
    <svg style={{ position: "absolute", left: x, top: y, transform: `scale(${s}) rotate(${t * 90}deg)` }}
      width={110} height={110} viewBox="-55 -55 110 110">
      <path d="M 0 -50 L 14 -15 L 50 -12 L 22 12 L 32 48 L 0 27 L -32 48 L -22 12 L -50 -12 L -14 -15 Z" fill={color} />
    </svg>
  );
};

// ── Subtitles (burned-in — kids watch muted too) ────────────────────────────

const SUBS: Array<{ from: number; dur: number; text: string }> = [
  { from: 195, dur: 165, text: "Once upon a time, in a big sandy desert, there lived a little camel named Cami." },
  { from: 360, dur: 105, text: "Cami loved to bounce. Boing! Boing! Boing!" },
  { from: 495, dur: 155, text: "One sunny day, Cami found something amazing… the great, big, blue sea!" },
  { from: 795, dur: 100, text: "Splash! Up popped a friendly fish named Finn." },
  { from: 900, dur: 85, text: "“Hello!” said Finn. “Let’s play!”" },
  { from: 1035, dur: 115, text: "They bounced a big beach ball, all afternoon long." },
  { from: 1395, dur: 140, text: "And as the sun went down, the two new best friends danced by the sea." },
  { from: 1635, dur: 95, text: "The end. See you next time, little star!" },
];

const Subtitles: React.FC = () => {
  const f = useCurrentFrame();
  const cue = SUBS.find((s) => f >= s.from && f < s.from + s.dur);
  if (!cue) return null;
  const t = (f - cue.from) / 8;
  const inS = Math.min(1, t);
  return (
    <div style={{
      position: "absolute", bottom: 210, left: 60, right: 60, textAlign: "center",
      transform: `scale(${0.9 + inS * 0.1})`, opacity: inS,
    }}>
      <span style={{
        display: "inline-block", background: "rgba(20,30,50,0.62)", color: "#FFFFFF",
        fontFamily: "'Liberation Sans', Arial, sans-serif", fontWeight: 700, fontSize: 44,
        lineHeight: 1.35, padding: "18px 34px", borderRadius: 28,
      }}>
        {cue.text}
      </span>
    </div>
  );
};

// ── Scenes ──────────────────────────────────────────────────────────────────

const Title: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const letters = "CAMI & FINN".split("");
  const fadeOut = interpolate(f, [150, 178], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: fadeOut }}>
      <div style={{ position: "absolute", top: 560, width: "100%", textAlign: "center" }}>
        {letters.map((ch, i) => {
          const s = spring({ frame: f - i * 4, fps, config: { damping: 9, mass: 0.6 } });
          return (
            <span key={i} style={{
              display: "inline-block", fontFamily: "'Liberation Sans', Arial, sans-serif",
              fontWeight: 800, fontSize: 150, color: i % 2 ? "#FF5A5F" : "#2C79C9",
              textShadow: "0 8px 0 rgba(0,0,0,0.14)",
              transform: `translateY(${(1 - s) * -420}px) rotate(${(1 - s) * 18}deg)`,
              width: ch === " " ? 44 : undefined,
            }}>{ch}</span>
          );
        })}
        <div style={{
          marginTop: 46, fontFamily: "'Liberation Sans', Arial, sans-serif", fontWeight: 700,
          fontSize: 52, color: "#5A4632",
          opacity: interpolate(f, [55, 80], [0, 1], clamp),
        }}>
          a tiny tale from the desert to the sea
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 8 } });
  const fade = interpolate(f, [150, 180], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: fade }}>
      <div style={{
        transform: `scale(${s})`, textAlign: "center",
        fontFamily: "'Liberation Sans', Arial, sans-serif", fontWeight: 800,
      }}>
        <div style={{ fontSize: 170, color: "#FFFFFF", textShadow: "0 10px 0 rgba(0,0,0,0.18)" }}>The End</div>
        <div style={{ fontSize: 64, color: "#FFF3C4", marginTop: 30 }}>★ see you next time, little star ★</div>
      </div>
    </AbsoluteFill>
  );
};

// ── The film ────────────────────────────────────────────────────────────────

export const Cartoon: React.FC = () => {
  const f = useCurrentFrame();

  // Cami's journey: bounces in place in S2, travels right during S3 toward the sea.
  const hopCycle = (f % 24) / 24;
  const camiX = f < S3 ? 120 : interpolate(f, [S3, S3 + 200], [120, 250], clamp);
  // Desert slides subtly left in S3 for the sense of travel; sea reveals.
  const seaReveal = interpolate(f, [S3 + 30, S3 + 140], [0, 1], { ...clamp, easing: Easing.inOut(Easing.ease) });
  const desertShift = interpolate(f, [S3, S3 + 200], [0, 300], clamp);

  // Finn pops at S4.
  const finnPop = interpolate(f, [S4 + 12, S4 + 40], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2.2)) });
  const splashT = interpolate(f, [S4 + 6, S4 + 40], [0, 1], clamp);

  // Beach ball rally in S5: ball arcs Cami(left, land) ↔ Finn(right, sea), 1.2s per leg.
  const rally = f >= S5 && f < S5 + 300;
  const leg = Math.floor((f - S5) / 36);
  const lt = ((f - S5) % 36) / 36;
  const goingRight = leg % 2 === 0;
  const bx = interpolate(goingRight ? lt : 1 - lt, [0, 1], [235, 700]);
  const by = 1130 - Math.sin(lt * Math.PI) * 330;
  const bSquash = lt < 0.06 || lt > 0.94 ? 0.82 : 1;

  // Sunset dance sway in S6.
  const sway = Math.sin(f / 8) * 30;

  // Cami hops only when bouncing matters (S2 intro + rally excitement + dance).
  const hop = f < S3 ? hopCycle : rally ? ((f % 36) / 36) : f >= S6 ? 0.5 + Math.sin(f / 8) * 0.08 : 0.02;

  return (
    <AbsoluteFill style={{ background: "#8ED4F7" }}>
      <Sky />
      <Sun />
      <Cloud y={180} scale={1.1} speed={0.9} offset={100} />
      <Cloud y={420} scale={0.8} speed={1.4} offset={900} />
      <Cloud y={90} scale={0.6} speed={0.6} offset={500} />
      <Desert shift={desertShift} />
      <Sea reveal={seaReveal} />

      {/* characters */}
      {f >= S2 - 20 && f < S7 && (
        <Camel x={camiX} y={1150} hop={hop} frame={f} flip={f >= S3 && f < S6 ? false : false} />
      )}
      {f >= S4 && f < S7 && (
        <div style={{ transform: f >= S6 ? `translateY(${-Math.abs(sway) / 2}px)` : undefined }}>
          <Fish x={640} y={1180} pop={finnPop} frame={f} />
        </div>
      )}
      <Splash t={splashT} x={560} y={1080} />

      {/* beach ball rally */}
      {rally && <BeachBall x={bx} y={by} rot={f * 6} squash={bSquash} />}
      {rally && lt < 0.2 && (
        <StarPop t={lt * 3} x={goingRight ? 300 : 760} y={goingRight ? 1080 : 1120}
          color={goingRight ? "#FFD93D" : "#FF8A5C"} />
      )}

      {/* sunset hearts */}
      {f >= S6 && f < S7 && (
        <>
          <StarPop t={((f - S6) % 70) / 70} x={430} y={900} color="#FF7BAC" />
          <StarPop t={((f - S6 + 35) % 70) / 70} x={620} y={820} color="#FFD93D" />
        </>
      )}

      {/* scene-level overlays */}
      <Sequence from={0} durationInFrames={S2}><Title /></Sequence>
      <Sequence from={S7} durationInFrames={180}><EndCard /></Sequence>
      <Subtitles />

      {/* gentle letterbox-free vignette for depth */}
      <AbsoluteFill style={{
        background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 62%, rgba(20,20,40,0.16) 100%)",
        pointerEvents: "none",
      }} />
    </AbsoluteFill>
  );
};
