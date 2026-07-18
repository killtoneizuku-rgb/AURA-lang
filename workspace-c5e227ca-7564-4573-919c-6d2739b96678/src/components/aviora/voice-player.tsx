// src/components/aviora/voice-player.tsx
// Standalone voice-player card — plays a single spoken line via the
// useVoiceSynthesis hook, with mute / replay controls and a live
// "speaking" indicator wired to the avatar-sync emotion.
//
// TypeScript rewrite of VoicePlayerExample.jsx using shadcn/ui Button.

"use client";

import { useEffect, useState } from "react";
import { Volume2, VolumeX, RotateCcw, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useVoiceSynthesis } from "@/hooks/use-voice-synthesis";
import { cn } from "@/lib/utils";
import type { Emotion } from "@/lib/aviora/types";

interface VoicePlayerProps {
  message: string;
  emotion?: Emotion;
  voiceId?: string;
  characterName?: string;
  /** When true, auto-speak whenever `message` changes. */
  autoSpeak?: boolean;
  className?: string;
}

export function VoicePlayer({
  message,
  emotion = "neutral",
  voiceId,
  characterName = "Aviora",
  autoSpeak = true,
  className,
}: VoicePlayerProps) {
  const [muted, setMuted] = useState(false);
  const { speak, stop, isLoading, isSpeaking, error } = useVoiceSynthesis();

  useEffect(() => {
    if (!autoSpeak) return;
    if (!muted && message) speak(message, { emotion, voiceId });
    return () => stop();
  }, [message]); // intentional: only re-speak when the message changes

  const toggleMute = () => {
    if (muted) {
      setMuted(false);
      speak(message, { emotion, voiceId });
    } else {
      setMuted(true);
      stop();
    }
  };

  return (
    <div
      className={cn(
        "rounded-2xl border border-rose-100 bg-gradient-to-br from-rose-50/80 via-white to-violet-50/80 p-4 shadow-sm",
        className
      )}
    >
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-semibold tracking-wide text-rose-900/80">
          {characterName}
        </span>
        <div className="flex gap-1.5">
          <Button
            onClick={toggleMute}
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full bg-rose-100/60 text-rose-600 hover:bg-rose-200/70 hover:text-rose-700"
            title={muted ? "Unmute" : "Mute"}
            aria-label={muted ? "Unmute voice" : "Mute voice"}
          >
            {muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
          </Button>
          <Button
            onClick={() => speak(message, { emotion, voiceId })}
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full bg-rose-100/60 text-rose-600 hover:bg-rose-200/70 hover:text-rose-700"
            title="Replay"
            aria-label="Replay voice"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <RotateCcw size={14} />
            )}
          </Button>
        </div>
      </div>

      <div className="rounded-xl bg-white px-4 py-3 text-[15px] leading-relaxed text-rose-950 shadow-[0_4px_14px_rgba(180,130,160,0.12)]">
        {message}
      </div>

      <div className="mt-2.5 flex items-center gap-2 text-xs text-rose-400">
        <span
          className={cn(
            "inline-block h-2 w-2 rounded-full transition-colors duration-200",
            isSpeaking
              ? "bg-rose-500 animate-pulse"
              : isLoading
              ? "bg-amber-400"
              : error
              ? "bg-red-400"
              : "bg-rose-200"
          )}
        />
        {isLoading
          ? "Generating voice…"
          : isSpeaking
          ? "Speaking…"
          : error
          ? "Voice unavailable — using browser fallback"
          : muted
          ? "Muted"
          : "Ready"}
      </div>
    </div>
  );
}
