# desert-sea-15s — platform test render

First end-to-end render on the integrated studio platform (docs/10): a 15.0s vertical
(1080×1920) test piece — desert → desert animals → desert wildlife → sea → sea life —
composed entirely from sourced Wikimedia Commons footage (PD / CC0 / CC-BY only, see
licenses.json), static-ffmpeg xfade cut, single pre-lapped ocean bed at −14 LUFS target.

Produced CPU-only, $0, per the core-profile doctrine. Generative engines (LTX-2 / Wan2.2 /
ComfyUI) were deliberately not used: no GPU on this host, and the sourced route is the
studio's own default. Deliverable: `out/desert-sea-15s.mp4` (out/ is untracked; assets/
downloads are untracked — sources.json records where every byte came from).

QC performed: ffprobe (15.000s, 1080×1920@30, h264 high + aac), ebur128 (−15.3 LUFS
integrated), frame extraction at all five shot midpoints reviewed, source letterbox in the
Mojave clip detected via cropdetect and removed before the vertical fill.
