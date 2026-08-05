import React from "react";
import { Composition } from "remotion";
import { Keeper, DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH } from "./Keeper";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Keeper"
    component={Keeper}
    durationInFrames={DURATION_IN_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
