// src/hooks/use-voice-synthesis.ts
// React hook that fetches TTS audio from the Aviora backend
// (POST /api/tts) and plays it, with graceful fallback to the browser's
// built-in SpeechSynthesis if the backend call fails or is unreachable.
//
// TypeScript port of useVoiceSynthesis.js, adapted to Next.js 16 + React 19.

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import type { Emotion } from "@/lib/aviora/types";

const DEFAULT_ENDPOINT = "/api/tts";

export interface UseVoiceSynthesisOptions {
  endpoint?: string;
  fallbackToBrowser?: boolean;
  /** e.g. "Samantha" — leave null for OS default. */
  browserVoiceName?: string | null;
}

export interface SpeakOptions {
  emotion?: Emotion;
  voiceId?: string;
}

export interface UseVoiceSynthesisResult {
  speak: (text: string, opts?: SpeakOptions) => Promise<void>;
  stop: () => void;
  audioUrl: string | null;
  isLoading: boolean;
  isSpeaking: boolean;
  error: string | null;
}

export function useVoiceSynthesis({
  endpoint = DEFAULT_ENDPOINT,
  fallbackToBrowser = true,
  browserVoiceName = null,
}: UseVoiceSynthesisOptions = {}): UseVoiceSynthesisResult {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const cleanupObjectUrl = useCallback(() => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, []);

  const speakWithBrowser = useCallback(
    (text: string) => {
      if (typeof window === "undefined" || !window.speechSynthesis) {
        setError("No TTS available in this environment");
        return;
      }
      const utterance = new SpeechSynthesisUtterance(text);
      if (browserVoiceName) {
        const match = window.speechSynthesis
          .getVoices()
          .find((v) => v.name === browserVoiceName);
        if (match) utterance.voice = match;
      }
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => {
        setIsSpeaking(false);
        setError("Browser speech synthesis failed");
      };
      window.speechSynthesis.speak(utterance);
    },
    [browserVoiceName]
  );

  const speak = useCallback(
    async (text: string, opts: SpeakOptions = {}): Promise<void> => {
      const { emotion = "neutral", voiceId } = opts;
      if (!text || !text.trim()) return;

      setError(null);
      stop();
      cleanupObjectUrl();

      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsLoading(true);
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, emotion, voiceId }),
          signal: controller.signal,
        });

        if (!res.ok) {
          throw new Error(`TTS request failed (${res.status})`);
        }

        const blob = await res.blob();
        if (blob.size === 0) {
          throw new Error("TTS returned an empty response");
        }
        const url = URL.createObjectURL(blob);
        objectUrlRef.current = url;
        setAudioUrl(url);

        const audio = new Audio(url);
        audioRef.current = audio;
        audio.onplay = () => setIsSpeaking(true);
        audio.onended = () => setIsSpeaking(false);
        audio.onpause = () => setIsSpeaking(false);
        audio.onerror = () => {
          setIsSpeaking(false);
          setError("Audio playback failed");
        };
        try {
          await audio.play();
        } catch (playErr) {
          // Autoplay blocked — the browser requires a user gesture before
          // audio can play. This happens on the very first auto-speak
          // after page load. Queue the audio to start on the next user
          // interaction (one-time listener) so the spoken line isn't lost.
          if (
            playErr instanceof DOMException &&
            (playErr.name === "NotAllowedError" || playErr.name === "SecurityError")
          ) {
            const resume = () => {
              audio.play().catch(() => {
                /* give up silently — user can hit replay */
              });
              document.removeEventListener("click", resume);
              document.removeEventListener("keydown", resume);
              document.removeEventListener("touchstart", resume);
            };
            document.addEventListener("click", resume, { once: true });
            document.addEventListener("keydown", resume, { once: true });
            document.addEventListener("touchstart", resume, { once: true });
            setError(null);
            return;
          }
          throw playErr;
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        console.error("[useVoiceSynthesis] error:", err);
        setError(err instanceof Error ? err.message : "Voice synthesis failed");
        if (fallbackToBrowser) speakWithBrowser(text);
      } finally {
        setIsLoading(false);
      }
    },
    [endpoint, stop, cleanupObjectUrl, fallbackToBrowser, speakWithBrowser]
  );

  // Clean up on unmount: revoke object URLs, abort in-flight requests, stop speech.
  useEffect(() => {
    return () => {
      cleanupObjectUrl();
      if (abortRef.current) abortRef.current.abort();
      if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [cleanupObjectUrl]);

  return { speak, stop, audioUrl, isLoading, isSpeaking, error };
}
