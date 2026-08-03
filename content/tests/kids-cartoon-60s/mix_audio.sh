#!/usr/bin/env bash
# Audio mix for kids-cartoon-60s — VO (Kokoro) + synthesized SFX + sea bed → 60s M4A.
# All SFX are ffmpeg aevalsrc synthesis ($0, no assets); the sea bed reuses the
# CC BY 3.0 Lækjavik waves audio from the desert-sea-15s test (licensed, recorded).
set -euo pipefail
cd "$(dirname "$0")"
FF=/home/user/ViralReel/vendor/ffbin/bin/ffmpeg
WAVES="../desert-sea-15s/assets/Ocean_waves_at_L%C3%A6kjavik_beach%2C_Iceland.webm"

$FF -hide_banner -loglevel error -y \
  -i vo/l1.wav -i vo/l2.wav -i vo/l3.wav -i vo/l4.wav \
  -i vo/l5.wav -i vo/l6.wav -i vo/l7.wav -i vo/l8.wav \
  -stream_loop 8 -i "$WAVES" \
  -f lavfi -i "aevalsrc=sin(2*PI*(300+900*t)*t)*exp(-7*t):d=0.4:s=48000" \
  -f lavfi -i "aevalsrc=(random(0)*2-1)*exp(-5*t):d=0.7:s=48000" \
  -f lavfi -i "aevalsrc=sin(2*PI*520*t)*exp(-16*t):d=0.16:s=48000" \
  -f lavfi -i "aevalsrc=sin(2*PI*660*t)*exp(-16*t):d=0.16:s=48000" \
  -f lavfi -i "aevalsrc=0.5*sin(2*PI*1318*t)*exp(-4*t)+0.5*sin(2*PI*1760*t)*exp(-5*t):d=0.9:s=48000" \
  -filter_complex "\
[0:a]aresample=48000,adelay=6500:all=1[vo1];\
[1:a]aresample=48000,adelay=12000:all=1[vo2];\
[2:a]aresample=48000,adelay=16500:all=1[vo3];\
[3:a]aresample=48000,adelay=26500:all=1[vo4];\
[4:a]aresample=48000,adelay=30000:all=1[vo5];\
[5:a]aresample=48000,adelay=34500:all=1[vo6];\
[6:a]aresample=48000,adelay=46500:all=1[vo7];\
[7:a]aresample=48000,adelay=54500:all=1[vo8];\
[8:a]aresample=48000,atrim=0:60,volume=0.22,afade=t=in:st=16:d=3,afade=t=out:st=58:d=2,adelay=0:all=1[bed];\
[9:a]asplit=3[bg1][bg2][bg3];\
[bg1]adelay=12200:all=1,volume=0.5[b1];[bg2]adelay=13000:all=1,volume=0.5[b2];[bg3]adelay=13800:all=1,volume=0.5[b3];\
[10:a]lowpass=f=2800,volume=0.8,adelay=26400:all=1[spl];\
[11:a]asplit=4[p1s][p2s][p3s][p4s];[12:a]asplit=4[q1s][q2s][q3s][q4s];\
[p1s]adelay=34800:all=1,volume=0.45[p1];[q1s]adelay=36000:all=1,volume=0.45[q1];\
[p2s]adelay=37200:all=1,volume=0.45[p2];[q2s]adelay=38400:all=1,volume=0.45[q2];\
[p3s]adelay=39600:all=1,volume=0.45[p3];[q3s]adelay=40800:all=1,volume=0.45[q3];\
[p4s]adelay=42000:all=1,volume=0.45[p4];[q4s]adelay=43200:all=1,volume=0.45[q4];\
[13:a]asplit=2[t1s][t2s];[t1s]adelay=54600:all=1,volume=0.6[t1];[t2s]adelay=56800:all=1,volume=0.5[t2];\
[vo1][vo2][vo3][vo4][vo5][vo6][vo7][vo8][bed][b1][b2][b3][spl][p1][q1][p2][q2][p3][q3][p4][q4][t1][t2]\
amix=inputs=23:normalize=0,loudnorm=I=-14:TP=-1:LRA=11,atrim=0:60,afade=t=out:st=58.5:d=1.5[aout]" \
  -map "[aout]" -c:a aac -b:a 192k audio60.m4a
echo "MIX_OK: $(pwd)/audio60.m4a"
