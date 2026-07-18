// src/lib/aviora/types.ts
// Shared type definitions for the Aviora character engine.
// These mirror the schema in the master system prompt — every field the LLM
// sees comes from one of these types, so type-safety here prevents drift.

export type Emotion =
  | "neutral"
  | "happy"
  | "sad"
  | "comforting"
  | "romantic"
  | "surprised"
  | "serious"
  | "shy";

export type RelationshipLevel =
  | "stranger"
  | "acquaintance"
  | "friend"
  | "close_friend"
  | "romantic_interest";

export interface CharacterProfile {
  name: string;
  age: number; // Must be 18+. Validated at load time.
  appearance: string;
  personality: string;
  backstory: string;
  speaking_style: string;
  likes: string[];
  dislikes: string[];
  relationship_level: RelationshipLevel;
  current_mood: string;
  current_emotion: Emotion;
  voice_style: string;
  world_setting: string;
  memories: string[];
  /** Optional explicit voice ID for the TTS engine (msedge-tts ShortName). */
  voice_id?: string;
}

/**
 * Avatar-sync metadata returned by the chat endpoint alongside the reply.
 * The `emotion` field is the SAME vocabulary used by EMOTION_PRESETS so a
 * single tag drives both the avatar's face and the TTS prosody.
 */
export interface AvatarMetadata {
  emotion: Emotion;
  expression: string;
  eye_movement: string;
  head_movement: string;
  posture: string;
  blink_rate: "slow" | "normal" | "fast";
  smile_intensity: number; // 0.0 – 1.0
  gesture?: string;
}

export type ChatRole = "system" | "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
  /** Only set on assistant messages — drives avatar face + TTS prosody. */
  metadata?: AvatarMetadata;
  /** ISO timestamp for client-side message ordering. */
  ts?: number;
}

export interface ChatRequest {
  messages: ChatMessage[];
  character: CharacterProfile;
}

export interface ChatResponse {
  reply: string;
  metadata: AvatarMetadata;
}

export interface TtsRequest {
  text: string;
  emotion?: Emotion;
  voiceId?: string;
}
