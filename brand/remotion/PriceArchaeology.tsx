/**
 * PriceArchaeology — the channel's Remotion composition.
 *
 * Consumes an episode's scene_plan.json verbatim as props (same field names the
 * motion-director writes: scenes[], with beat / in / out / asset / transform /
 * text[] / odometer / stamp / shows_price / citation) plus a VO file and caption
 * chunks. Implements the bible's visual system: archive on the bottom, data on
 * top; amber past / cyan present; one odometer; a stamped verdict; a citation
 * chip on every price frame (gate C3 extracts frames and checks).
 *
 * LIVES IN THE STUDIO REPO. scripts/render_episode.sh copies this file and
 * ./PriceOdometer.tsx into vendor/openmontage/remotion-composer/src/ at render
 * time and registers the composition — the vendor clone is never committed to,
 * and a fresh clone re-materialises everything from here.
 *
 * Colour values are read from PA_TOKENS in PriceOdometer.tsx (single source in
 * TS-land, itself locked to config/channel.yaml).
 */

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {PriceOdometer, PA_TOKENS, PA_FONT_STACK} from './PriceOdometer';

/* ---------- prop types (mirror scene_plan.json, no invention) ---------- */

type TextLayer = {
  content: string;
  token?: 'past' | 'present' | 'alarm' | 'data';
  size?: 'hero' | 'body';
};

type Scene = {
  id: string;
  beat: string;
  in: number;
  out: number;
  asset: string; // filename relative to public/<slug>/
  transform?: {crop?: string; desaturate?: number; push?: number};
  text?: TextLayer[];
  odometer?: {from: number; to: number; duration_ms?: number; currency?: string};
  stamp?: {word: string; token?: string; rotation_deg?: number};
  shows_price?: boolean;
  citation?: string;
};

export type PriceArchaeologyProps = {
  slug: string;
  scenes: Scene[];
  voSrc: string; // relative to public/<slug>/
  captions?: {text: string; start: number; end: number}[];
};

/* ------------------------------ helpers ------------------------------ */

const isVideo = (f: string) => /\.(mp4|webm|mov|mkv|m4v)$/i.test(f);

const tokenColor = (t?: string) =>
  t === 'past' ? PA_TOKENS.past
  : t === 'present' ? PA_TOKENS.present
  : t === 'alarm' ? PA_TOKENS.alarm
  : t === 'extinct' ? '#848484'
  : PA_TOKENS.data;

/** Full-bleed archival layer: centre-cropped 9:16, desaturated, slow push. */
const MediaLayer: React.FC<{scene: Scene; slug: string; localFrame: number; fps: number}> = ({
  scene, slug, localFrame, fps,
}) => {
  const dur = Math.max(1, (scene.out - scene.in) * fps);
  const push = scene.transform?.push ?? 1.04;
  const scale = interpolate(localFrame, [0, dur], [1, push], {
    extrapolateRight: 'clamp',
  });
  const desat = scene.transform?.desaturate ?? 0.4;
  const src = staticFile(`${slug}/${scene.asset}`);
  const style: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transform: `scale(${scale})`,
    // bible §5: footage desaturated to ~40% with slight grain; grain comes from
    // the sources themselves (real archival), contrast pulled down a touch.
    filter: `saturate(${1 - desat}) contrast(0.96)`,
  };
  return (
    <AbsoluteFill style={{backgroundColor: PA_TOKENS.ground}}>
      {isVideo(scene.asset) ? (
        <OffthreadVideo src={src} style={style} muted />
      ) : (
        <Img src={src} style={style} />
      )}
      {/* legibility scrim behind the data layer — flat, no vignette drama */}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(180deg, rgba(10,10,10,0.35) 0%, rgba(10,10,10,0.05) 40%, rgba(10,10,10,0.45) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};

/** The inspector's rubber stamp: hard-edged, rotated, 2px shake on entry. */
const Stamp: React.FC<{word: string; color: string; rotationDeg: number; localFrame: number}> = ({
  word, color, rotationDeg, localFrame,
}) => {
  // impact: visible from frame 3 of its scene, shakes ±2px for ~5 frames
  if (localFrame < 3) return null;
  const shake = localFrame < 8 ? (localFrame % 2 === 0 ? 2 : -2) : 0;
  return (
    <div
      style={{
        border: `10px solid ${color}`,
        boxShadow: `inset 0 0 0 4px ${PA_TOKENS.ground}, inset 0 0 0 7px ${color}`,
        color,
        fontFamily: PA_FONT_STACK,
        fontWeight: 900,
        fontSize: 96,
        letterSpacing: '0.08em',
        padding: '28px 48px',
        transform: `rotate(${rotationDeg}deg) translate(${shake}px, 0)`,
        textTransform: 'uppercase',
        background: 'rgba(10,10,10,0.25)',
      }}
    >
      {word}
    </div>
  );
};

/* ----------------------------- composition ----------------------------- */

export const PriceArchaeology: React.FC<PriceArchaeologyProps> = ({
  slug, scenes, voSrc, captions = [],
}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const t = frame / fps;

  const activeCaption = captions.find((c) => t >= c.start && t < c.end);

  return (
    <AbsoluteFill style={{backgroundColor: PA_TOKENS.ground, fontFamily: PA_FONT_STACK}}>
      {scenes.map((scene) => {
        const from = Math.round(scene.in * fps);
        const durF = Math.max(1, Math.round((scene.out - scene.in) * fps));
        return (
          <Sequence key={scene.id} from={from} durationInFrames={durF}>
            <SceneView scene={scene} slug={slug} width={width} />
          </Sequence>
        );
      })}

      {/* captions — most Shorts play muted. Above the platform UI band. */}
      {activeCaption ? (
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
            }}
          >
            {activeCaption.text}
          </div>
        </AbsoluteFill>
      ) : null}

      <Audio src={staticFile(`${slug}/${voSrc}`)} />
    </AbsoluteFill>
  );
};

const SceneView: React.FC<{scene: Scene; slug: string; width: number}> = ({scene, slug, width}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill>
      <MediaLayer scene={scene} slug={slug} localFrame={frame} fps={fps} />

      {/* data layer */}
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

        {(scene.text ?? []).map((layer, i) => (
          <div
            key={i}
            style={{
              color: tokenColor(layer.token),
              fontFamily: PA_FONT_STACK,
              fontWeight: layer.size === 'hero' ? 900 : 400,
              fontSize: layer.size === 'hero' ? 152 : 54,
              lineHeight: 1.08,
              textAlign: 'center',
              fontVariantNumeric: 'tabular-nums lining-nums',
              fontFeatureSettings: '"tnum" 1, "lnum" 1',
              textShadow: '0 2px 16px rgba(10,10,10,0.85)',
              marginTop: i === 0 && !scene.odometer ? 0 : 24,
              maxWidth: '92%',
            }}
          >
            {layer.content}
          </div>
        ))}

        {scene.stamp ? (
          <Stamp
            word={scene.stamp.word}
            color={tokenColor(scene.stamp.token)}
            rotationDeg={scene.stamp.rotation_deg ?? 4}
            localFrame={frame}
          />
        ) : null}
      </AbsoluteFill>

      {/* citation chip — museum placard. Present whenever a price is on screen.
          Ugly is acceptable; absent is not (gate C3 extracts frames and checks). */}
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
            }}
          >
            {scene.citation}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
