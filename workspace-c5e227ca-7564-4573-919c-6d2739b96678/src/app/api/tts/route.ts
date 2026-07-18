// src/app/api/tts/route.ts
// Aviora voice backend — Microsoft Edge neural voices via msedge-tts.
// TypeScript port of server-tts.js, adapted to Next.js 16 App Router.
//
// No API key needed. Runs server-side only — Edge's Read Aloud API now
// requires an Edge-browser user agent, so this MUST stay off the client.
//
// POST /api/tts
//   body: { text: string, emotion?: Emotion, voiceId?: string }
//   → 200 audio/mpeg  |  400 {error}  |  502 {error}

import { NextRequest, NextResponse } from "next/server";
import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";

import { EMOTION_PRESETS } from "@/lib/aviora/emotion-presets";
import type { Emotion, TtsRequest } from "@/lib/aviora/types";

export const runtime = "nodejs";
// TTS synthesis is per-utterance and stateless on our side — let the
// platform cache aggressively so a replay of the same line is instant.
export const dynamic = "force-dynamic";

const DEFAULT_VOICE = "en-US-JennyNeural";
const MAX_TEXT_LEN = 1200;

function escapeForSSML(text: string): string {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function isEmotion(v: unknown): v is Emotion {
  return (
    typeof v === "string" &&
    [
      "neutral",
      "happy",
      "sad",
      "comforting",
      "romantic",
      "surprised",
      "serious",
      "shy",
    ].includes(v)
  );
}

export async function POST(req: NextRequest) {
  let body: TtsRequest;
  try {
    body = (await req.json()) as TtsRequest;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const text = body?.text;
  if (!text || !text.trim()) {
    return NextResponse.json({ error: "text is required" }, { status: 400 });
  }
  if (text.length > MAX_TEXT_LEN) {
    return NextResponse.json(
      { error: `text too long for a single utterance (max ${MAX_TEXT_LEN} chars)` },
      { status: 400 }
    );
  }

  const emotion: Emotion = isEmotion(body.emotion) ? body.emotion : "neutral";
  const prosody = EMOTION_PRESETS[emotion] ?? EMOTION_PRESETS.neutral;
  const voice = body.voiceId || DEFAULT_VOICE;
  const safeText = escapeForSSML(text);

  let tts: MsEdgeTTS | null = null;
  try {
    tts = new MsEdgeTTS();
    await tts.setMetadata(
      voice,
      OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3
    );
    // NOTE: toStream() is synchronous in msedge-tts v2 — it returns
    // { audioStream, metadataStream } directly. `await`-ing a non-Promise
    // is harmless (returns the value), so we keep it for forward-compat.
    const { audioStream } = await (tts.toStream as unknown as (
      input: string,
      options: typeof prosody
    ) => Promise<{ audioStream: NodeJS.ReadableStream }> | {
      audioStream: NodeJS.ReadableStream;
    })(safeText, prosody);

    const chunks: Buffer[] = await new Promise<Buffer[]>((resolve, reject) => {
      const out: Buffer[] = [];
      audioStream.on("data", (chunk: Buffer) => out.push(chunk));
      audioStream.on("end", () => resolve(out));
      audioStream.on("close", () => resolve(out));
      audioStream.on("error", (err: Error) => reject(err));
    });

    const audio = Buffer.concat(chunks);
    if (audio.length === 0) {
      throw new Error("Edge TTS returned an empty audio stream");
    }

    return new NextResponse(audio, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Length": String(audio.length),
        "Cache-Control": "public, max-age=86400, immutable",
      },
    });
  } catch (err) {
    console.error("[/api/tts] Edge TTS error:", err);
    return NextResponse.json(
      { error: "voice synthesis failed", detail: (err as Error)?.message },
      { status: 502 }
    );
  } finally {
    // Always close the WS so we don't leak connections across requests.
    try {
      tts?.close();
    } catch {
      /* ignore — best-effort cleanup */
    }
  }
}

export async function GET() {
  return NextResponse.json({
    ok: true,
    endpoint: "POST /api/tts",
    body: {
      text: "string (required, max 1200 chars)",
      emotion:
        "neutral | happy | sad | comforting | romantic | surprised | serious | shy",
      voiceId: "string (optional msedge-tts ShortName, default en-US-JennyNeural)",
    },
    response: "audio/mpeg",
  });
}
