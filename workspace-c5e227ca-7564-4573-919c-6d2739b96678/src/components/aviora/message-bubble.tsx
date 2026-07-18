// src/components/aviora/message-bubble.tsx
// A single chat message bubble. User messages align right (rose), companion
// messages align left (with avatar portrait + voice controls + emotion chip).

"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { AvatarMetadata, ChatMessage } from "@/lib/aviora/types";
import { AvatarPortrait } from "./avatar-portrait";
import { VoicePlayer } from "./voice-player";

interface MessageBubbleProps {
  message: ChatMessage;
  characterName: string;
  voiceId?: string;
  isLastAssistant?: boolean;
}

const EMOTION_LABEL: Record<AvatarMetadata["emotion"], string> = {
  neutral: "calm",
  happy: "happy",
  sad: "tender",
  comforting: "comforting",
  romantic: "soft",
  surprised: "surprised",
  serious: "serious",
  shy: "shy",
};

const EMOTION_CHIP: Record<AvatarMetadata["emotion"], string> = {
  neutral: "bg-rose-100 text-rose-700",
  happy: "bg-amber-100 text-amber-700",
  sad: "bg-slate-100 text-slate-600",
  comforting: "bg-rose-100 text-rose-700",
  romantic: "bg-pink-100 text-pink-700",
  surprised: "bg-orange-100 text-orange-700",
  serious: "bg-violet-100 text-violet-700",
  shy: "bg-fuchsia-100 text-fuchsia-700",
};

export function MessageBubble({
  message,
  characterName,
  voiceId,
  isLastAssistant = false,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        className="flex justify-end"
      >
        <div className="max-w-[78%] rounded-2xl rounded-br-md bg-gradient-to-br from-rose-500 to-rose-600 px-4 py-2.5 text-[15px] leading-relaxed text-white shadow-[0_4px_14px_rgba(217,140,166,0.35)]">
          {message.content}
        </div>
      </motion.div>
    );
  }

  const metadata = message.metadata;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="flex gap-3"
    >
      <div className="h-12 w-12 shrink-0">
        {metadata && (
          <AvatarPortrait
            metadata={metadata}
            name={characterName}
            className="h-12 w-12"
          />
        )}
      </div>
      <div className="flex max-w-[80%] flex-col gap-1.5">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-rose-900/70">
            {characterName}
          </span>
          {metadata && (
            <span
              className={cn(
                "rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide",
                EMOTION_CHIP[metadata.emotion]
              )}
            >
              {EMOTION_LABEL[metadata.emotion]}
            </span>
          )}
        </div>
        <div className="rounded-2xl rounded-tl-md border border-rose-100/70 bg-white px-4 py-2.5 text-[15px] leading-relaxed text-rose-950 shadow-sm">
          {message.content}
        </div>
        {isLastAssistant && message.content && (
          <VoicePlayer
            message={message.content}
            emotion={metadata?.emotion ?? "neutral"}
            voiceId={voiceId}
            characterName={characterName}
            className="!rounded-xl !p-0 !bg-transparent !border-0 !shadow-none"
          />
        )}
      </div>
    </motion.div>
  );
}
