import React from "react";
import { Composition } from "remotion";
import { Wild, DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH } from "./Wild";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Wild"
    component={Wild}
    durationInFrames={DURATION_IN_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
