// src/components/aviora/companion-chat.tsx
// Full Aviora companion chat: history + composer + live avatar portrait
// panel. Calls POST /api/chat for companion replies, then auto-speaks the
// reply via useVoiceSynthesis.

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Send, Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useVoiceSynthesis } from "@/hooks/use-voice-synthesis";
import { AvatarPortrait } from "./avatar-portrait";
import { MessageBubble } from "./message-bubble";
import {
  AVIORA_CHARACTER,
  VOICE_PICKER_SHORTLIST,
} from "@/lib/aviora/character";
import { avatarBaseline } from "@/lib/aviora/emotion-presets";
import type {
  AvatarMetadata,
  ChatMessage,
  CharacterProfile,
} from "@/lib/aviora/types";

interface CompanionChatProps {
  character?: CharacterProfile;
}

const INITIAL_GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi there. I'm glad you stopped by tonight — it's quiet here, and quiet is good for talking. What's on your mind?",
  metadata: avatarBaseline("happy"),
  ts: Date.now(),
};

export function CompanionChat({
  character = AVIORA_CHARACTER,
}: CompanionChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [voiceId, setVoiceId] = useState<string>(
    character.voice_id ?? VOICE_PICKER_SHORTLIST[0].id
  );
  const [liveMetadata, setLiveMetadata] = useState<AvatarMetadata>(
    avatarBaseline(character.current_emotion)
  );

  const voice = useVoiceSynthesis();
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to the latest message.
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  // Auto-speak the latest assistant reply.
  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");
  useEffect(() => {
    if (!lastAssistant || !lastAssistant.content) return;
    if (lastAssistant.ts && Date.now() - lastAssistant.ts > 5000) return;
    setLiveMetadata(
      lastAssistant.metadata ?? avatarBaseline(character.current_emotion)
    );
    voice.speak(lastAssistant.content, {
      emotion: lastAssistant.metadata?.emotion ?? "neutral",
      voiceId,
    });
  }, [lastAssistant?.ts]);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || busy) return;

    const userMsg: ChatMessage = {
      role: "user",
      content: text,
      ts: Date.now(),
    };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setBusy(true);
    setLiveMetadata(avatarBaseline("neutral"));

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: nextMessages.map((m) => ({ role: m.role, content: m.content })),
          character,
        }),
      });
      if (!res.ok) {
        throw new Error(`chat failed (${res.status})`);
      }
      const data = (await res.json()) as { reply: string; metadata: AvatarMetadata };
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: data.reply,
        metadata: data.metadata,
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error("[companion-chat] send failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Hmm... something snagged on my end for a second. Could you say that again?",
          metadata: avatarBaseline("sad"),
          ts: Date.now(),
        },
      ]);
    } finally {
      setBusy(false);
    }
  }, [input, busy, messages, character]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  };

  const lastAssistantTs = lastAssistant?.ts;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      {/* Chat column */}
      <div className="flex h-[calc(100vh-12rem)] min-h-[520px] flex-col rounded-3xl border border-rose-100 bg-white/70 shadow-[0_10px_40px_-12px_rgba(180,130,160,0.25)] backdrop-blur">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-rose-100 px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-rose-950">{character.name}</h2>
            <p className="text-xs text-rose-400">
              {character.current_mood}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "inline-block h-2 w-2 rounded-full",
                voice.isSpeaking
                  ? "bg-rose-500 animate-pulse"
                  : voice.isLoading
                  ? "bg-amber-400"
                  : "bg-rose-200"
              )}
            />
            <span className="text-xs text-rose-400">
              {voice.isSpeaking
                ? "speaking"
                : voice.isLoading
                ? "generating voice"
                : "voice ready"}
            </span>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1" ref={scrollRef as never}>
          <div className="flex flex-col gap-4 p-5">
            <AnimatePresence initial={false}>
              {messages.map((m, i) => (
                <MessageBubble
                  key={i}
                  message={m}
                  characterName={character.name}
                  voiceId={voiceId}
                  isLastAssistant={
                    m.role === "assistant" && m.ts === lastAssistantTs
                  }
                />
              ))}
            </AnimatePresence>
            {busy && (
              <div className="flex gap-3">
                <div className="h-12 w-12 shrink-0" />
                <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-md border border-rose-100/70 bg-white px-4 py-3 shadow-sm">
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-rose-400 [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-rose-400 [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-rose-400" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Composer */}
        <div className="border-t border-rose-100 p-4">
          <div className="flex items-end gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder={`Talk to ${character.name}…`}
              rows={2}
              className="resize-none border-rose-100 bg-white/80 text-[15px] text-rose-950 placeholder:text-rose-300 focus-visible:ring-rose-300"
              disabled={busy}
            />
            <Button
              onClick={() => void send()}
              disabled={busy || !input.trim()}
              className="h-10 w-10 shrink-0 rounded-xl bg-gradient-to-br from-rose-500 to-rose-600 text-white shadow-[0_4px_14px_rgba(217,140,166,0.4)] hover:from-rose-600 hover:to-rose-700"
              aria-label="Send message"
            >
              {busy ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
            </Button>
          </div>
          <p className="mt-2 text-[11px] text-rose-300">
            Enter to send · Shift+Enter for a new line
          </p>
        </div>
      </div>

      {/* Side panel: avatar + character + voice picker */}
      <aside className="flex flex-col gap-4">
        <div className="rounded-3xl border border-rose-100 bg-gradient-to-br from-rose-50 via-white to-violet-50 p-5 shadow-sm">
          <div className="mx-auto aspect-square w-full max-w-[220px]">
            <AvatarPortrait
              metadata={liveMetadata}
              name={character.name}
              speaking={voice.isSpeaking}
              className="h-full w-full"
            />
          </div>
          <div className="mt-4 space-y-1.5 text-center">
            <div className="flex items-center justify-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              <span className="text-base font-semibold text-rose-950">
                {character.name}
              </span>
            </div>
            <p className="text-xs text-rose-500">{character.voice_style}</p>
          </div>
          <div className="mt-4 rounded-xl bg-white/70 p-3">
            <p className="text-[11px] uppercase tracking-wide text-rose-400">
              Now feeling
            </p>
            <p className="mt-1 text-sm font-medium text-rose-900">
              {liveMetadata.expression}
            </p>
            <div className="mt-2 grid grid-cols-2 gap-1 text-[11px] text-rose-500">
              <span>eyes: {liveMetadata.eye_movement}</span>
              <span>head: {liveMetadata.head_movement}</span>
              <span>posture: {liveMetadata.posture}</span>
              <span>blink: {liveMetadata.blink_rate}</span>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-rose-100 bg-white/70 p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-rose-950">Voice</h3>
          <div className="flex flex-col gap-1.5">
            {VOICE_PICKER_SHORTLIST.map((v) => (
              <button
                key={v.id}
                onClick={() => setVoiceId(v.id)}
                className={cn(
                  "flex items-center justify-between rounded-xl border px-3 py-2 text-left transition-colors",
                  voiceId === v.id
                    ? "border-rose-300 bg-rose-50"
                    : "border-rose-100 hover:border-rose-200 hover:bg-rose-50/50"
                )}
              >
                <div>
                  <div className="text-sm font-medium text-rose-950">{v.label}</div>
                  <div className="text-[11px] text-rose-400">{v.description}</div>
                </div>
                {voiceId === v.id && (
                  <span className="h-2 w-2 rounded-full bg-rose-500" />
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-rose-100 bg-white/70 p-5 shadow-sm">
          <h3 className="mb-2 text-sm font-semibold text-rose-950">About</h3>
          <p className="text-xs leading-relaxed text-rose-600">
            {character.backstory}
          </p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {character.likes.slice(0, 4).map((like) => (
              <span
                key={like}
                className="rounded-full bg-rose-50 px-2 py-0.5 text-[10px] text-rose-500"
              >
                {like}
              </span>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
