/**
 * PriceOdometer — the signature move.
 *
 * Owner: brand-designer. Spec: docs/02-channel-bible.md §5, config/channel.yaml → brand.*
 *
 * A price rolls mechanically from the anchor-year figure to the current-year figure over
 * ~800ms with an ease-out, while the colour crosses from amber-past to cyan-present. One
 * motion, used identically in every episode, is what makes the channel recognisable
 * mid-scroll at 2× speed. Ownable motion beats varied motion.
 *
 * THINGS THIS COMPONENT DELIBERATELY DOES NOT EXPOSE
 *   · colour        — amber→cyan is the channel's colour grammar, not a per-episode choice
 *   · easing        — one curve, forever
 *   · spring physics — springs are frame-rate-expressive and bouncy; an odometer is a machine
 * If you find yourself wanting a prop for any of those, the answer is upstream: change the
 * bible and change it for all episodes, or don't change it.
 *
 * WHY DIGIT WHEELS AND NOT A FORMATTED STRING
 *   Re-rendering `value.toFixed()` every frame relies on the font for stability. Wheels are
 *   stable by construction: every digit lives in its own fixed-width, overflow-hidden slot,
 *   the slot count is fixed for the whole shot, and leading zeros are hidden with opacity
 *   rather than removed — so nothing reflows mid-roll. Tabular figures are still enforced
 *   (see the container style) because they are what make the slots equal width in the first
 *   place; proportional digits make an odometer jitter, and jitter reads as cheap.
 *
 * RENDER DETERMINISM
 *   Separators are explicit props, not Intl output. Two machines with different ICU builds
 *   must produce byte-identical frames.
 */

import React, {useMemo} from 'react';
import {
  Easing,
  interpolate,
  interpolateColors,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/**
 * Locked colour tokens, mirrored from config/channel.yaml → brand.colors.
 * channel.yaml is the source of truth; if these ever diverge, this file is the bug.
 * Kept as TS constants rather than CSS custom properties because interpolateColors needs
 * real values to mix — `var(--pa-color-past)` cannot be interpolated.
 */
export const PA_TOKENS = {
  past: '#C8964B', // every 2016 figure
  present: '#00E5FF', // every 2026 figure
  alarm: '#FF3B30', // deltas above +100% only
  ground: '#0A0A0A',
  data: '#FFFFFF',
} as const;

/** config/channel.yaml → brand.odometer_ms */
export const PA_ODOMETER_MS = 800;

/** Mirrors --pa-font-grotesque in brand/tokens.css. See that file re: the licensed family. */
export const PA_FONT_STACK =
  '"Helvetica Neue", Helvetica, Arial, "Liberation Sans", "Nimbus Sans", system-ui, sans-serif';

/** --pa-text-number: the hero number, 4× body. */
const DEFAULT_FONT_SIZE = 176;

/** A wheel shows 0–9 and then 0 again, so the wrap from 9 to 0 rolls instead of jumping. */
const WHEEL_FACES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];

export type PriceOdometerProps = {
  /** The anchor-year figure, in major currency units (e.g. 159 or 159.99). Must be >= 0. */
  from: number;
  /** The current-year figure, in major currency units. Must be >= 0. */
  to: number;
  /** Rendered verbatim next to the number — e.g. "$", "£", "€". No symbol is inferred. */
  currency: string;
  /**
   * Roll duration. Defaults to config/channel.yaml → brand.odometer_ms (800).
   * The prop exists so the config value can be threaded through, not so an episode can
   * decide it feels better at 1200.
   */
  durationMs?: number;
  /** Frames to wait before the roll starts, expressed in ms. The number sits at `from`. */
  delayMs?: number;
  /** Decimal places. Defaults to 0 when both figures are integers, otherwise 2. */
  decimals?: number;
  /** Pixel size of the digits. Defaults to --pa-text-number (176). */
  fontSize?: number;
  /** Wheel height as a multiple of fontSize. Defaults to --pa-leading-number (1). */
  lineHeightRatio?: number;
  currencyPosition?: 'prefix' | 'suffix';
  groupSeparator?: string;
  decimalSeparator?: string;
  className?: string;
  /** Escape hatch for layout only (margins, alignment). Colour and motion are not yours. */
  style?: React.CSSProperties;
};

type Slot =
  | {kind: 'digit'; key: string; exponent: number}
  | {kind: 'glyph'; key: string; char: string; hideBelow: number | null};

/**
 * Formats a value the same way the wheels display it. Exported so callers can build
 * captions, alt text and citation chips from the identical string.
 */
export const formatPriceValue = (
  value: number,
  decimals: number,
  groupSeparator = ',',
  decimalSeparator = '.',
): string => {
  const fixed = Math.abs(value).toFixed(decimals);
  const [integerPart, fractionPart] = fixed.split('.');
  const grouped = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, groupSeparator);
  return `${value < 0 ? '-' : ''}${grouped}${fractionPart ? decimalSeparator + fractionPart : ''}`;
};

/** Number of digits in the integer part of the larger of the two figures. */
const integerDigitCount = (value: number): number =>
  Math.max(1, Math.floor(value).toString().length);

/**
 * Where a wheel sits, in units of one face height, within [0, 10).
 *
 * `wheelIndex` counts up from the least significant displayed digit (0 = the wheel that
 * spins continuously — that is the whole texture of the move). Every wheel above it stays
 * locked and only turns while the wheels below it complete their final unit: the tens wheel
 * carries across the last 1/10 of its turn, the hundreds across the last 1/100, and so on.
 *
 * The narrowing window is the part that matters. A fixed 10% window would start dragging the
 * hundreds digit at 890 instead of 899, and — with cents on screen — would leave the units
 * wheel sitting 90% rolled at a dead stop on $9.99. A price at rest must read as a crisp
 * digit; only a price in motion is allowed to smear.
 */
const wheelPosition = (raw: number, wheelIndex: number): number => {
  const whole = Math.floor(raw);
  const fraction = raw - whole;
  const window = Math.pow(10, -wheelIndex);
  const carry = Math.min(1, Math.max(0, (fraction - (1 - window)) / window));
  return (((whole % 10) + 10) % 10) + carry;
};

const DigitWheel: React.FC<{
  position: number;
  faceHeight: number;
  hidden: boolean;
}> = ({position, faceHeight, hidden}) => (
  <span
    style={{
      display: 'inline-block',
      height: faceHeight,
      overflow: 'hidden',
      opacity: hidden ? 0 : 1,
    }}
  >
    <span
      style={{
        display: 'block',
        transform: `translateY(${-position * faceHeight}px)`,
        willChange: 'transform',
      }}
    >
      {WHEEL_FACES.map((face, index) => (
        <span
          // eslint-disable-next-line react/no-array-index-key -- fixed-length static reel
          key={index}
          style={{
            display: 'block',
            height: faceHeight,
            lineHeight: `${faceHeight}px`,
            textAlign: 'center',
          }}
        >
          {face}
        </span>
      ))}
    </span>
  </span>
);

export const PriceOdometer: React.FC<PriceOdometerProps> = ({
  from,
  to,
  currency,
  durationMs = PA_ODOMETER_MS,
  delayMs = 0,
  decimals,
  fontSize = DEFAULT_FONT_SIZE,
  lineHeightRatio = 1,
  currencyPosition = 'prefix',
  groupSeparator = ',',
  decimalSeparator = '.',
  className,
  style,
}) => {
  // Validated before any hook runs, so the hook order is identical on every render that
  // survives. A bad figure should fail the render loudly rather than roll to NaN.
  if (!Number.isFinite(from) || !Number.isFinite(to)) {
    throw new Error('PriceOdometer: `from` and `to` must be finite numbers.');
  }
  if (from < 0 || to < 0) {
    throw new Error(
      'PriceOdometer: `from` and `to` must be >= 0. This renders prices, not deltas.',
    );
  }

  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const resolvedDecimals =
    decimals ?? (Number.isInteger(from) && Number.isInteger(to) ? 0 : 2);

  const delayInFrames = Math.round((delayMs / 1000) * fps);
  const durationInFrames = Math.max(1, Math.round((durationMs / 1000) * fps));

  // Ease-out, no spring. This bezier is the SAME curve as --pa-odometer-ease in
  // tokens.css — they are one motion expressed in two languages and must not drift.
  // (An earlier version used Easing.out(Easing.cubic) here, which is a materially
  // different curve from the CSS token, so anything styled from CSS did not match.)
  const progress = interpolate(
    frame,
    [delayInFrames, delayInFrames + durationInFrames],
    [0, 1],
    {
      easing: Easing.bezier(0.16, 1, 0.3, 1),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );

  const value = from + (to - from) * progress;

  // Amber past -> cyan present, on the same eased clock as the roll. The number finishes
  // arriving and finishes changing colour on the same frame.
  //
  // Exception, per the channel bible: a delta above +100% lands on `alarm` instead of
  // `present`. Without this the alarm token had no rendering path anywhere in the system —
  // a bible rule with no implementation is a silent compliance gap.
  const deltaRatio = from === 0 ? Infinity : (to - from) / Math.abs(from);
  const destination = deltaRatio > 1 ? PA_TOKENS.alarm : PA_TOKENS.present;
  const color = interpolateColors(progress, [0, 1], [PA_TOKENS.past, destination]);

  const faceHeight = Math.round(fontSize * lineHeightRatio);
  const scale = Math.pow(10, resolvedDecimals);

  // Round away float noise so that progress === 1 lands on exactly `to`
  // (2.99 * 100 is 298.99999999999994, which would floor to a displayed 2.98).
  const scaled = Math.round(value * scale * 1e6) / 1e6;

  // What the wheels are actually showing this frame. Leading-zero and separator visibility
  // is decided from this, not from the raw value, so the "$" can never step across a column
  // one frame before the digit it belongs to appears.
  const displayValue = scaled / scale;

  // Digits and separators only — the currency mark is placed during the render pass,
  // because where it belongs depends on how many leading zeros are hidden this frame.
  const slots = useMemo<Slot[]>(() => {
    const intDigits = integerDigitCount(Math.max(from, to));
    const out: Slot[] = [];

    for (let exponent = intDigits - 1; exponent >= 0; exponent--) {
      out.push({kind: 'digit', key: `d${exponent}`, exponent});
      if (exponent > 0 && exponent % 3 === 0) {
        // The separator disappears with the group it separates, so 999 never renders ",999".
        out.push({
          kind: 'glyph',
          key: `group${exponent}`,
          char: groupSeparator,
          hideBelow: Math.pow(10, exponent),
        });
      }
    }

    if (resolvedDecimals > 0) {
      out.push({kind: 'glyph', key: 'point', char: decimalSeparator, hideBelow: null});
      for (let exponent = -1; exponent >= -resolvedDecimals; exponent--) {
        out.push({kind: 'digit', key: `d${exponent}`, exponent});
      }
    }

    return out;
  }, [from, to, groupSeparator, decimalSeparator, resolvedDecimals]);

  // A slot is hidden when it belongs to a leading group the current value has not reached.
  // Hidden means opacity 0, never unmounted: the slot keeps its width, so a digit column
  // never moves sideways when the number crosses a power of ten.
  const isHidden = (slot: Slot): boolean =>
    slot.kind === 'glyph'
      ? slot.hideBelow !== null && displayValue < slot.hideBelow
      : slot.exponent >= 1 && displayValue < Math.pow(10, slot.exponent);

  // The currency mark goes immediately before the first *visible* digit rather than at the
  // far left, so "$" never floats away from its number across blank leading slots. The
  // reordering only permutes the slots ahead of the first visible digit, so the sum of
  // widths before it — and therefore the x of every digit — is unchanged. When the number
  // gains a digit mid-roll the mark steps one column left, which is the only thing that
  // moves.
  const firstVisibleIndex = slots.findIndex((slot) => !isHidden(slot));

  const currencyGlyph = currency ? (
    <span
      key="currency"
      style={{
        display: 'inline-block',
        height: faceHeight,
        lineHeight: `${faceHeight}px`,
      }}
    >
      {currency}
    </span>
  ) : null;

  const children: React.ReactNode[] = [];

  slots.forEach((slot, index) => {
    if (currencyPosition === 'prefix' && index === firstVisibleIndex && currencyGlyph) {
      children.push(currencyGlyph);
    }

    if (slot.kind === 'glyph') {
      children.push(
        <span
          key={slot.key}
          style={{
            display: 'inline-block',
            height: faceHeight,
            lineHeight: `${faceHeight}px`,
            opacity: isHidden(slot) ? 0 : 1,
          }}
        >
          {slot.char}
        </span>,
      );
      return;
    }

    const wheelIndex = slot.exponent + resolvedDecimals; // 0 = least significant wheel
    children.push(
      <DigitWheel
        key={slot.key}
        faceHeight={faceHeight}
        position={wheelPosition(scaled / Math.pow(10, wheelIndex), wheelIndex)}
        hidden={isHidden(slot)}
      />,
    );
  });

  if (currencyPosition === 'suffix' && currencyGlyph) {
    children.push(currencyGlyph);
  }

  const ariaLabel = `${currencyPosition === 'prefix' ? currency : ''}${formatPriceValue(
    to,
    resolvedDecimals,
    groupSeparator,
    decimalSeparator,
  )}${currencyPosition === 'suffix' ? currency : ''}`;

  return (
    <span
      className={className}
      aria-label={ariaLabel}
      style={{
        display: 'inline-flex',
        alignItems: 'flex-start',
        color,
        fontFamily: PA_FONT_STACK,
        fontSize,
        fontWeight: 700,
        lineHeight: `${faceHeight}px`,
        letterSpacing: '-0.01em',
        // TABULAR FIGURES. Both properties on purpose: the high-level one for fonts that
        // map it, the raw feature for fonts that only expose "tnum".
        fontVariantNumeric: 'tabular-nums lining-nums',
        fontFeatureSettings: '"tnum" 1, "lnum" 1',
        fontKerning: 'none',
        whiteSpace: 'nowrap',
        // Data layer: flat and sharp. No shadow, no glow, ever.
        textShadow: 'none',
        ...style,
      }}
    >
      {children}
    </span>
  );
};

export default PriceOdometer;
