// src/components/aviora/avatar-portrait.tsx
// Pure-CSS avatar portrait whose pose is driven by AvatarMetadata.
// No image assets needed — the portrait is composed from layered divs so
// expression, eye movement, head tilt, and blink rate all animate smoothly
// from the metadata block returned alongside each companion reply.

"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { AvatarMetadata } from "@/lib/aviora/types";

interface AvatarPortraitProps {
  metadata: AvatarMetadata;
  name: string;
  speaking?: boolean;
  className?: string;
}

// Map emotion → base palette so the portrait's aura also reflects mood.
const EMOTION_PALETTE: Record<AvatarMetadata["emotion"], { aura: string; tint: string }> = {
  neutral: { aura: "rgba(217, 140, 166, 0.18)", tint: "#F3D9E4" },
  happy: { aura: "rgba(255, 196, 217, 0.35)", tint: "#FFD3E2" },
  sad: { aura: "rgba(155, 138, 168, 0.25)", tint: "#C9BCD6" },
  comforting: { aura: "rgba(243, 217, 228, 0.35)", tint: "#F3D9E4" },
  romantic: { aura: "rgba(255, 184, 209, 0.45)", tint: "#FFC2D6" },
  surprised: { aura: "rgba(255, 224, 178, 0.35)", tint: "#FFE0B2" },
  serious: { aura: "rgba(155, 138, 168, 0.2)", tint: "#B7A6C7" },
  shy: { aura: "rgba(255, 200, 210, 0.4)", tint: "#FFC8D2" },
};

const HEAD_TILT: Record<string, string> = {
  "slight tilt": "rotate(-4deg)",
  "small nod": "rotate(0deg)",
  "slight dip": "rotate(2deg) translateY(2px)",
  "small lift": "rotate(0deg) translateY(-2px)",
  still: "rotate(0deg)",
};

const EYE_OFFSET: Record<string, { x: number; y: number }> = {
  "direct gaze": { x: 0, y: 0 },
  "soft gaze": { x: 0, y: 1 },
  "lingering gaze": { x: 0, y: 0 },
  "wide gaze": { x: 0, y: -1 },
  "steady gaze": { x: 0, y: 0 },
  "glancing away": { x: 3, y: 0 },
  "looking down": { x: 0, y: 3 },
};

export function AvatarPortrait({
  metadata,
  name,
  speaking = false,
  className,
}: AvatarPortraitProps) {
  const palette = EMOTION_PALETTE[metadata.emotion] ?? EMOTION_PALETTE.neutral;
  const tilt = HEAD_TILT[metadata.head_movement] ?? HEAD_TILT.still;
  const eye = EYE_OFFSET[metadata.eye_movement] ?? EYE_OFFSET["direct gaze"];
  const blinkDur =
    metadata.blink_rate === "fast" ? 1.4 : metadata.blink_rate === "slow" ? 5 : 3;

  // Smile intensity → mouth curvature. 0.0 = flat, 1.0 = full smile.
  const smile = metadata.smile_intensity ?? 0.4;
  const mouthCurve = -6 * smile - 2; // negative = upward curve in SVG

  return (
    <div
      className={cn("relative flex items-center justify-center", className)}
      aria-label={`${name} portrait — ${metadata.expression}`}
      role="img"
    >
      {/* Soft mood aura */}
      <motion.div
        className="absolute inset-0 rounded-full blur-2xl"
        animate={{
          backgroundColor: palette.aura,
          scale: speaking ? 1.08 : 1,
        }}
        transition={{ duration: 1.4, ease: "easeInOut" }}
      />

      {/* Portrait frame */}
      <div className="relative h-full w-full overflow-hidden rounded-3xl border border-white/60 bg-gradient-to-b from-rose-50 via-white to-violet-50 shadow-[0_18px_50px_-12px_rgba(180,130,160,0.4)]">
        {/* Decorative stars */}
        <div className="pointer-events-none absolute inset-0 opacity-50">
          <Star className="absolute left-3 top-4 h-2 w-2 text-amber-300" />
          <Star className="absolute right-4 top-6 h-1.5 w-1.5 text-rose-300" />
          <Star className="absolute left-6 bottom-8 h-1 w-1 text-violet-300" />
          <Star className="absolute right-3 bottom-4 h-1.5 w-1.5 text-amber-200" />
        </div>

        {/* Head group */}
        <motion.div
          className="absolute left-1/2 top-1/2 origin-bottom"
          style={{ x: "-50%", y: "-45%" }}
          animate={{ transform: tilt }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          {/* Hair back layer */}
          <div
            className="absolute left-1/2 top-1/2 h-32 w-32 -translate-x-1/2 -translate-y-1/2 rounded-[42%] bg-gradient-to-b from-rose-300 via-rose-400 to-violet-300"
            style={{ filter: "blur(0.5px)" }}
          />

          {/* Face */}
          <div className="relative h-24 w-24 rounded-full bg-gradient-to-b from-rose-50 to-rose-100 shadow-[inset_0_-6px_12px_rgba(217,140,166,0.18)]">
            {/* Hair front fringe */}
            <div className="absolute -top-2 left-1/2 h-12 w-28 -translate-x-1/2 rounded-t-full bg-gradient-to-b from-rose-300 to-rose-400 opacity-90" />
            <div className="absolute -top-1 left-3 h-10 w-6 rounded-full bg-rose-400/80" />
            <div className="absolute -top-1 right-3 h-10 w-6 rounded-full bg-rose-400/80" />

            {/* Star hairpin */}
            <div className="absolute -right-1 top-2">
              <Star className="h-3 w-3 text-amber-400" />
            </div>

            {/* Eyes */}
            <div className="absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 gap-4">
              <Eye
                blinkDur={blinkDur}
                offsetX={eye.x}
                offsetY={eye.y}
                speaking={speaking}
              />
              <Eye
                blinkDur={blinkDur}
                offsetX={eye.x}
                offsetY={eye.y}
                speaking={speaking}
              />
            </div>

            {/* Blush (shy / romantic) */}
            {(metadata.emotion === "shy" || metadata.emotion === "romantic") && (
              <>
                <div className="absolute left-3 top-12 h-3 w-5 rounded-full bg-rose-300/50" />
                <div className="absolute right-3 top-12 h-3 w-5 rounded-full bg-rose-300/50" />
              </>
            )}

            {/* Mouth */}
            <svg
              className="absolute left-1/2 top-[60%] -translate-x-1/2"
              width="28"
              height="10"
              viewBox="0 0 28 10"
              fill="none"
              aria-hidden="true"
            >
              <path
                d={`M2 ${5 + mouthCurve / 2} Q14 ${10 + mouthCurve} 26 ${5 + mouthCurve / 2}`}
                stroke="#C25A7A"
                strokeWidth="2"
                strokeLinecap="round"
                fill={smile > 0.6 ? "#E07A99" : "none"}
                fillOpacity={0.4}
              />
            </svg>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Eye({
  blinkDur,
  offsetX,
  offsetY,
  speaking,
}: {
  blinkDur: number;
  offsetX: number;
  offsetY: number;
  speaking: boolean;
}) {
  return (
    <motion.div
      className="relative h-3 w-3 rounded-full bg-amber-700"
      animate={{
        scaleY: [1, 1, 0.1, 1, 1],
        x: offsetX,
        y: offsetY,
      }}
      transition={{
        scaleY: {
          duration: blinkDur,
          repeat: Infinity,
          ease: "easeInOut",
          times: [0, 0.45, 0.5, 0.55, 1],
        },
        x: { duration: 0.6, ease: "easeOut" },
        y: { duration: 0.6, ease: "easeOut" },
      }}
    >
      <div
        className={cn(
          "absolute left-1/2 top-1/2 h-1 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white",
          speaking && "animate-pulse"
        )}
      />
    </motion.div>
  );
}

function Star({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 12 12"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M6 0l1.5 3.5L11 5l-3.5 1.5L6 10l-1.5-3.5L1 5l3.5-1.5L6 0z" />
    </svg>
  );
}
