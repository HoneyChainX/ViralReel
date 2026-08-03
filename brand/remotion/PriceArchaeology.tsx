/**
 * PriceArchaeology — the channel's Remotion composition. v2.
 *
 * v2 exists because the founder watched v1 and said the motion was sparse, the
 * images repeated, and it didn't feel documentary-grade. Fair. v2 adds, all
 * within the brand system and gate rules:
 *   - per-scene entry transitions (fade / dip-to-black / slide)
 *   - a directional Ken Burns engine (in/out/left/right/up/down) replacing the
 *     uniform slow push that made every scene feel identical
 *   - ANIMATED evidence charts (bars grow, figures count up, every bar cited) —
 *     "designed support" per the hybrid pipeline; the static chart PNG remains
 *     only as the held C1 receipt
 *   - kinetic text (rise / pop / type-on), staggered
 *   - procedural film grain + vignette on footage scenes (grading, not content)
 *   - stamp impact: flash + decaying shake
 *
 * Compliance line unchanged (docs/05-compliance.md Rule 6): the archive layer is
 * never synthesised — motion here is typography, charts and grading over real,
 * licensed media. Colour/motion tokens: PriceOdometer.tsx (locked to channel.yaml).
 */

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {PriceOdometer, PA_TOKENS, PA_FONT_STACK} from './PriceOdometer';

/* ---------- the one easing (mirrors --pa-odometer-ease) ---------- */
const EASE = Easing.bezier(0.16, 1, 0.3, 1);

/* ---------- prop types (mirror scene_plan.json v2) ---------- */

type TextLayer = {
  content: string;
  token?: 'past' | 'present' | 'alarm' | 'data';
  size?: 'hero' | 'body';
  anim?: 'rise' | 'pop' | 'typeon';
};

type ChartBar = {
  label: string;
  value: number;
  color: 'past' | 'present' | 'pastAdj';
  cite?: string;
};

type Scene = {
  id: string;
  beat: string;
  in: number;
  out: number;
  asset?: string;
  transform?: {crop?: string; desaturate?: number; push?: number; fit?: 'cover' | 'contain'};
  transition?: {type: 'fade' | 'dip' | 'slide'; dur?: number};
  kenburns?: {dir: 'in' | 'out' | 'left' | 'right' | 'up' | 'down'; amount?: number};
  text?: TextLayer[];
  textAnim?: 'rise' | 'pop' | 'typeon';
  odometer?: {from: number; to: number; duration_ms?: number; currency?: string};
  stamp?: {word: string; token?: string; rotation_deg?: number};
  chart?: {bars: ChartBar[]; title?: string};
  shows_price?: boolean;
  citation?: string;
};

export type PriceArchaeologyProps = {
  slug: string;
  scenes: Scene[];
  voSrc: string;
  captions?: {text: string; start: number; end: number}[];
};

/* ------------------------------ helpers ------------------------------ */

const isVideo = (f: string) => /\.(mp4|webm|mov|mkv|m4v)$/i.test(f);

const tokenColor = (t?: string) =>
  t === 'past' ? PA_TOKENS.past
  : t === 'present' ? PA_TOKENS.present
  : t === 'alarm' ? PA_TOKENS.alarm
  : t === 'pastAdj' ? '#8A6534'
  : t === 'extinct' ? '#848484'
  : PA_TOKENS.data;

const fmtMoney = (v: number) => {
  const hasCents = Math.abs(v - Math.round(v)) > 0.004;
  return '$' + v.toLocaleString('en-US', {
    minimumFractionDigits: hasCents ? 2 : 0,
    maximumFractionDigits: hasCents ? 2 : 0,
  });
};

/** Directional Ken Burns: scale + translate, one deliberate move per scene. */
const kenburnsStyle = (
  dir: string, amount: number, progress: number,
): React.CSSProperties => {
  const zIn = 1 + (amount - 1) * progress;
  const zOut = amount - (amount - 1) * progress;
  const panPct = (amount - 1) * 50; // translate budget derived from zoom headroom
  switch (dir) {
    case 'in':    return {transform: `scale(${zIn})`};
    case 'out':   return {transform: `scale(${zOut})`};
    case 'left':  return {transform: `scale(${amount}) translateX(${panPct * (1 - 2 * progress)}px)`};
    case 'right': return {transform: `scale(${amount}) translateX(${-panPct * (1 - 2 * progress)}px)`};
    case 'up':    return {transform: `scale(${amount}) translateY(${panPct * (1 - 2 * progress)}px)`};
    case 'down':  return {transform: `scale(${amount}) translateY(${-panPct * (1 - 2 * progress)}px)`};
    default:      return {transform: `scale(${zIn})`};
  }
};

/** Procedural grain: a noise tile nudged every frame + a quiet vignette.
    This is grading — it adds no content, it unifies mixed-era footage. */
const NOISE_TILE =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240">
       <filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
       <feColorMatrix type="saturate" values="0"/></filter>
       <rect width="240" height="240" filter="url(#n)" opacity="0.55"/>
     </svg>`,
  );

const Grain: React.FC<{frame: number}> = ({frame}) => (
  <>
    <AbsoluteFill
      style={{
        backgroundImage: `url("${NOISE_TILE}")`,
        backgroundRepeat: 'repeat',
        backgroundPosition: `${(frame * 37) % 240}px ${(frame * 61) % 240}px`,
        opacity: 0.055,
        mixBlendMode: 'overlay',
        pointerEvents: 'none',
      }}
    />
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(ellipse 90% 75% at 50% 46%, rgba(0,0,0,0) 62%, rgba(10,10,10,0.42) 100%)',
        pointerEvents: 'none',
      }}
    />
  </>
);

/* --------------------------- kinetic text --------------------------- */

const AnimatedText: React.FC<{
  layer: TextLayer;
  localFrame: number;
  fps: number;
  delayFrames: number;
}> = ({layer, localFrame, fps, delayFrames}) => {
  const anim = layer.anim ?? 'rise';
  const t = Math.max(0, localFrame - delayFrames);
  const base: React.CSSProperties = {
    color: tokenColor(layer.token),
    fontFamily: PA_FONT_STACK,
    fontWeight: layer.size === 'hero' ? 900 : 400,
    fontSize: layer.size === 'hero' ? 152 : 54,
    lineHeight: 1.08,
    textAlign: 'center',
    fontVariantNumeric: 'tabular-nums lining-nums',
    fontFeatureSettings: '"tnum" 1, "lnum" 1',
    textShadow: '0 2px 16px rgba(10,10,10,0.85)',
    marginTop: 24,
    maxWidth: '92%',
  };

  if (anim === 'typeon') {
    const chars = Math.floor(interpolate(t, [0, fps * 0.7], [0, layer.content.length], {
      extrapolateRight: 'clamp',
    }));
    return <div style={base}>{layer.content.slice(0, Math.max(0, chars))}</div>;
  }
  if (anim === 'pop') {
    const s = interpolate(t, [0, fps * 0.28], [0.6, 1], {easing: EASE, extrapolateRight: 'clamp'});
    const o = interpolate(t, [0, fps * 0.18], [0, 1], {extrapolateRight: 'clamp'});
    return <div style={{...base, transform: `scale(${s})`, opacity: o}}>{layer.content}</div>;
  }
  // rise
  const y = interpolate(t, [0, fps * 0.4], [34, 0], {easing: EASE, extrapolateRight: 'clamp'});
  const o = interpolate(t, [0, fps * 0.3], [0, 1], {extrapolateRight: 'clamp'});
  return <div style={{...base, transform: `translateY(${y}px)`, opacity: o}}>{layer.content}</div>;
};

/* --------------------------- animated chart --------------------------- */

const AnimatedChart: React.FC<{
  chart: NonNullable<Scene['chart']>;
  localFrame: number;
  fps: number;
}> = ({chart, localFrame, fps}) => {
  const max = Math.max(...chart.bars.map((b) => b.value)) * 1.08;
  return (
    <div style={{width: '88%', fontFamily: PA_FONT_STACK}}>
      {chart.title ? (
        <div style={{
          color: PA_TOKENS.data, fontSize: 46, fontWeight: 900, marginBottom: 34,
          textShadow: '0 2px 12px rgba(10,10,10,0.9)',
        }}>
          {chart.title}
        </div>
      ) : null}
      {chart.bars.map((bar, i) => {
        const start = i * Math.round(fps * 0.28);
        const t = Math.max(0, localFrame - start);
        const p = interpolate(t, [0, fps * 0.85], [0, 1], {easing: EASE, extrapolateRight: 'clamp'});
        const shown = bar.value * p;
        const color = tokenColor(bar.color);
        return (
          <div key={i} style={{marginBottom: 26}}>
            <div style={{
              color: PA_TOKENS.data, opacity: 0.92, fontSize: 30, marginBottom: 8,
              textShadow: '0 1px 8px rgba(10,10,10,0.9)',
            }}>
              {bar.label}
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
              <div style={{
                height: 44,
                width: `${(bar.value / max) * 100 * p}%`,
                background: bar.color === 'pastAdj'
                  ? `repeating-linear-gradient(135deg, ${color}, ${color} 10px, rgba(10,10,10,0.35) 10px, rgba(10,10,10,0.35) 18px)`
                  : color,
                boxShadow: '0 2px 10px rgba(10,10,10,0.6)',
              }} />
              <div style={{
                color, fontSize: 40, fontWeight: 900, whiteSpace: 'nowrap',
                fontVariantNumeric: 'tabular-nums lining-nums',
                fontFeatureSettings: '"tnum" 1',
                textShadow: '0 1px 10px rgba(10,10,10,0.9)',
              }}>
                {fmtMoney(shown)}
              </div>
            </div>
            {bar.cite && p > 0.96 ? (
              <div style={{color: PA_TOKENS.data, opacity: 0.5, fontSize: 21, marginTop: 5}}>
                {bar.cite}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
};

/* ------------------------------- stamp ------------------------------- */

const Stamp: React.FC<{word: string; color: string; rotationDeg: number; localFrame: number; fps: number}> = ({
  word, color, rotationDeg, localFrame, fps,
}) => {
  if (localFrame < 2) return null;
  const t = localFrame - 2;
  // impact: overshoot scale-down, decaying shake, one flash frame
  const scale = interpolate(t, [0, fps * 0.14], [1.5, 1], {easing: EASE, extrapolateRight: 'clamp'});
  const decay = Math.max(0, 1 - t / (fps * 0.35));
  const shake = decay > 0 ? Math.sin(t * 2.4) * 3.2 * decay : 0;
  const flash = t < 2;
  return (
    <>
      {flash ? <AbsoluteFill style={{background: color, opacity: 0.14}} /> : null}
      <div
        style={{
          border: `10px solid ${color}`,
          boxShadow: `inset 0 0 0 4px ${PA_TOKENS.ground}, inset 0 0 0 7px ${color}, 0 6px 40px rgba(10,10,10,0.55)`,
          color,
          fontFamily: PA_FONT_STACK,
          fontWeight: 900,
          fontSize: 96,
          letterSpacing: '0.08em',
          padding: '28px 48px',
          transform: `rotate(${rotationDeg}deg) scale(${scale}) translate(${shake}px, 0)`,
          textTransform: 'uppercase',
          background: 'rgba(10,10,10,0.25)',
        }}
      >
        {word}
      </div>
    </>
  );
};

/* ----------------------------- media layer ----------------------------- */

const MediaLayer: React.FC<{scene: Scene; slug: string; localFrame: number; fps: number; durF: number}> = ({
  scene, slug, localFrame, fps, durF,
}) => {
  if (!scene.asset) return <AbsoluteFill style={{backgroundColor: PA_TOKENS.ground}} />;
  const fit = scene.transform?.fit ?? 'cover';
  const desat = scene.transform?.desaturate ?? 0.4;
  const progress = interpolate(localFrame, [0, durF], [0, 1]);
  const kb = scene.kenburns ?? {dir: 'in', amount: scene.transform?.push ?? 1.06};
  const motion = fit === 'contain'
    ? kenburnsStyle(kb.dir === 'out' ? 'out' : 'in', Math.min(kb.amount ?? 1.05, 1.06), progress)
    : kenburnsStyle(kb.dir, kb.amount ?? 1.08, progress);
  const src = staticFile(`${slug}/${scene.asset}`);
  const style: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: fit,
    ...motion,
    filter: fit === 'contain' ? 'none' : `saturate(${1 - desat}) contrast(0.96)`,
  };
  return (
    <AbsoluteFill style={{backgroundColor: PA_TOKENS.ground}}>
      {isVideo(scene.asset) ? (
        <OffthreadVideo src={src} style={style} muted />
      ) : (
        <Img src={src} style={style} />
      )}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(180deg, rgba(10,10,10,0.35) 0%, rgba(10,10,10,0.05) 40%, rgba(10,10,10,0.45) 100%)',
        }}
      />
      {fit === 'cover' ? <Grain frame={localFrame} /> : null}
    </AbsoluteFill>
  );
};

/* ------------------------------ scene view ------------------------------ */

const SceneView: React.FC<{scene: Scene; slug: string; width: number}> = ({scene, slug, width}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const durF = Math.max(1, Math.round((scene.out - scene.in) * fps));

  // entry transition
  const tr = scene.transition;
  const trF = Math.round((tr?.dur ?? 0.3) * fps);
  let opacity = 1;
  let slideX = 0;
  let dip = 0;
  if (tr?.type === 'fade') opacity = interpolate(frame, [0, trF], [0, 1], {extrapolateRight: 'clamp'});
  if (tr?.type === 'slide') slideX = interpolate(frame, [0, trF], [width * 0.06, 0], {easing: EASE, extrapolateRight: 'clamp'});
  if (tr?.type === 'dip') dip = interpolate(frame, [0, trF], [1, 0], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{opacity, transform: slideX ? `translateX(${slideX}px)` : undefined}}>
      <MediaLayer scene={scene} slug={slug} localFrame={frame} fps={fps} durF={durF} />

      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 64}}>
        {scene.odometer ? (
          <PriceOdometer
            from={scene.odometer.from}
            to={scene.odometer.to}
            currency={scene.odometer.currency ?? '$'}
            durationMs={scene.odometer.duration_ms ?? 800}
            delayMs={400}
            fontSize={width >= 1080 ? 176 : 132}
          />
        ) : null}

        {scene.chart ? <AnimatedChart chart={scene.chart} localFrame={frame} fps={fps} /> : null}

        {(scene.text ?? []).map((layer, i) => (
          <AnimatedText
            key={i}
            layer={{...layer, anim: layer.anim ?? scene.textAnim}}
            localFrame={frame}
            fps={fps}
            delayFrames={i * Math.round(fps * 0.12)}
          />
        ))}

        {scene.stamp ? (
          <Stamp
            word={scene.stamp.word}
            color={tokenColor(scene.stamp.token)}
            rotationDeg={scene.stamp.rotation_deg ?? 4}
            localFrame={frame}
            fps={fps}
          />
        ) : null}
      </AbsoluteFill>

      {scene.shows_price && scene.citation ? (
        <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'flex-start'}}>
          <div
            style={{
              margin: '0 0 96px 40px',
              color: PA_TOKENS.data,
              opacity: 0.6,
              fontSize: 26,
              fontWeight: 400,
              fontFamily: PA_FONT_STACK,
              background: 'rgba(10,10,10,0.55)',
              padding: '8px 14px',
              maxWidth: '88%',
            }}
          >
            {scene.citation}
          </div>
        </AbsoluteFill>
      ) : null}

      {dip > 0 ? <AbsoluteFill style={{background: PA_TOKENS.ground, opacity: dip}} /> : null}
    </AbsoluteFill>
  );
};

/* ----------------------------- composition ----------------------------- */

export const PriceArchaeology: React.FC<PriceArchaeologyProps> = ({
  slug, scenes, voSrc, captions = [],
}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const t = frame / fps;
  const cap = captions.find((c) => t >= c.start && t < c.end);
  const capT = cap ? (t - cap.start) * fps : 0;
  const capY = cap ? interpolate(capT, [0, fps * 0.22], [16, 0], {easing: EASE, extrapolateRight: 'clamp'}) : 0;
  const capO = cap ? interpolate(capT, [0, fps * 0.18], [0, 1], {extrapolateRight: 'clamp'}) : 0;

  return (
    <AbsoluteFill style={{backgroundColor: PA_TOKENS.ground, fontFamily: PA_FONT_STACK}}>
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={Math.round(scene.in * fps)}
          durationInFrames={Math.max(1, Math.round((scene.out - scene.in) * fps))}
        >
          <SceneView scene={scene} slug={slug} width={width} />
        </Sequence>
      ))}

      {cap ? (
        <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center'}}>
          <div
            style={{
              marginBottom: 420,
              maxWidth: '86%',
              textAlign: 'center',
              color: PA_TOKENS.data,
              fontSize: 44,
              fontWeight: 400,
              lineHeight: 1.25,
              textShadow: '0 2px 12px rgba(10,10,10,0.9), 0 0 4px rgba(10,10,10,0.9)',
              transform: `translateY(${capY}px)`,
              opacity: capO,
            }}
          >
            {cap.text}
          </div>
        </AbsoluteFill>
      ) : null}

      <Audio src={staticFile(`${slug}/${voSrc}`)} />
    </AbsoluteFill>
  );
};
