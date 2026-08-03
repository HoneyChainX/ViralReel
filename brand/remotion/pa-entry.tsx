/**
 * Dedicated Remotion entry for Price Archaeology renders.
 *
 * The vendor's src/index.tsx registers every OpenMontage composition, and several
 * of those import @remotion/google-fonts — which fetches from fonts.gstatic.com at
 * page load. In an egress-blocked environment those fetches fail and Remotion
 * treats it as a fatal NetworkError. Registering ONLY our composition keeps the
 * render fully offline: system font stack, staticFile() media, nothing external.
 *
 * scripts/render_episode.sh copies this to vendor .../src/pa-entry.tsx and renders:
 *   npx remotion render src/pa-entry.tsx PriceArchaeology ...
 */

import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {PriceArchaeology} from './PriceArchaeology';

const FPS = 30;

const PARoot: React.FC = () => (
  <Composition
    id="PriceArchaeology"
    component={PriceArchaeology}
    durationInFrames={FPS * 45}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{slug: '', scenes: [], voSrc: 'vo.mp3', captions: []}}
    calculateMetadata={({props}) => {
      const scenes = (props.scenes ?? []) as {out?: number}[];
      const end = scenes.reduce((m, s) => Math.max(m, s.out ?? 0), 0);
      return {durationInFrames: Math.max(FPS, Math.round((end + 0.2) * FPS))};
    }}
  />
);

registerRoot(PARoot);
