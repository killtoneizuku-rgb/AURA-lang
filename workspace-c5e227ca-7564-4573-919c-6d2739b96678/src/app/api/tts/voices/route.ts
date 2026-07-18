// src/app/api/tts/voices/route.ts
// Exposes the live voice catalog so a frontend voice-picker always matches
// what Microsoft currently offers, instead of a hardcoded list.
//
// GET /api/tts/voices → 200 Voice[] | 502 {error}

import { NextResponse } from "next/server";
import { MsEdgeTTS, type Voice } from "msedge-tts";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// In-process cache — voice catalog doesn't change per-request, and
// msedge-tts.getVoices() makes an HTTP call to Microsoft each time.
let cached: Voice[] | null = null;
let cachedAt = 0;
const CACHE_TTL_MS = 1000 * 60 * 60; // 1 hour

export async function GET() {
  if (cached && Date.now() - cachedAt < CACHE_TTL_MS) {
    return NextResponse.json({ voices: cached });
  }

  const tts = new MsEdgeTTS();
  try {
    const voices = await tts.getVoices();
    cached = voices;
    cachedAt = Date.now();
    return NextResponse.json({ voices });
  } catch (err) {
    console.error("[/api/tts/voices] getVoices error:", err);
    return NextResponse.json(
      { error: "could not fetch voice list" },
      { status: 502 }
    );
  } finally {
    try {
      tts.close();
    } catch {
      /* ignore */
    }
  }
}
