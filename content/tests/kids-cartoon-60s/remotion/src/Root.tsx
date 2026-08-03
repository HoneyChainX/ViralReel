import React from "react";
import { Composition } from "remotion";
import { Cartoon, DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH } from "./Cartoon";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Cartoon"
    component={Cartoon}
    durationInFrames={DURATION_IN_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
