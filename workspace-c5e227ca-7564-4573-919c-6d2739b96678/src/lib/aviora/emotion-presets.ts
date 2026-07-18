// src/lib/aviora/emotion-presets.ts
// One tag drives both the avatar's face and the voice's prosody.
// Keys match the `emotion` field used by AvatarMetadata + the TTS endpoint
// so the LLM never has to translate between vocabularies.

import type { Emotion, AvatarMetadata } from "./types";

/**
 * Prosody options accepted by msedge-tts's `toStream(input, options)`.
 * `rate` and `pitch` use the relative-percentage / relative-Hz format that
 * SSML understands natively — no manual XML escaping needed here.
 */
export interface ProsodyPreset {
  rate: string; // e.g. "+10%"
  pitch: string; // e.g. "+35Hz"
  volume?: string; // e.g. "+0%"
}

export const EMOTION_PRESETS: Record<Emotion, ProsodyPreset> = {
  neutral: { rate: "+0%", pitch: "+0Hz", volume: "+0%" },
  happy: { rate: "+10%", pitch: "+35Hz", volume: "+5%" },
  sad: { rate: "-12%", pitch: "-20Hz", volume: "-10%" },
  comforting: { rate: "-8%", pitch: "-8Hz", volume: "+5%" },
  romantic: { rate: "-10%", pitch: "+8Hz", volume: "+0%" },
  surprised: { rate: "+12%", pitch: "+45Hz", volume: "+10%" },
  serious: { rate: "-4%", pitch: "-15Hz", volume: "+0%" },
  shy: { rate: "-6%", pitch: "+15Hz", volume: "-5%" },
};

/**
 * Default avatar pose for each emotion. The chat endpoint may override these
 * per-message — this is just the baseline used when the LLM doesn't emit
 * explicit avatar metadata.
 */
export const AVATAR_BASELINE: Record<Emotion, Omit<AvatarMetadata, "emotion">> = {
  neutral: {
    expression: "calm, attentive gaze",
    eye_movement: "direct gaze",
    head_movement: "still",
    posture: "relaxed upright",
    blink_rate: "normal",
    smile_intensity: 0.35,
  },
  happy: {
    expression: "soft smile, bright eyes",
    eye_movement: "direct gaze",
    head_movement: "small nod",
    posture: "leaning in",
    blink_rate: "normal",
    smile_intensity: 0.75,
  },
  sad: {
    expression: "gentle concern, soft frown",
    eye_movement: "looking down",
    head_movement: "slight dip",
    posture: "shoulders relaxed, leaning back",
    blink_rate: "slow",
    smile_intensity: 0.1,
  },
  comforting: {
    expression: "warm, reassuring smile",
    eye_movement: "soft gaze",
    head_movement: "slight tilt",
    posture: "leaning in",
    blink_rate: "slow",
    smile_intensity: 0.55,
  },
  romantic: {
    expression: "tender, half-lidded eyes",
    eye_movement: "lingering gaze",
    head_movement: "slight tilt",
    posture: "leaning close",
    blink_rate: "slow",
    smile_intensity: 0.6,
  },
  surprised: {
    expression: "wide eyes, raised brows",
    eye_movement: "wide gaze",
    head_movement: "small lift",
    posture: "alert",
    blink_rate: "fast",
    smile_intensity: 0.4,
  },
  serious: {
    expression: "focused, level gaze",
    eye_movement: "steady gaze",
    head_movement: "still",
    posture: "upright",
    blink_rate: "slow",
    smile_intensity: 0.15,
  },
  shy: {
    expression: "blush, small smile",
    eye_movement: "glancing away",
    head_movement: "slight duck",
    posture: "hunched slightly",
    blink_rate: "fast",
    smile_intensity: 0.3,
  },
};

export function avatarBaseline(emotion: Emotion): AvatarMetadata {
  return { emotion, ...AVATAR_BASELINE[emotion] };
}

export const ALL_EMOTIONS: Emotion[] = [
  "neutral",
  "happy",
  "sad",
  "comforting",
  "romantic",
  "surprised",
  "serious",
  "shy",
];
