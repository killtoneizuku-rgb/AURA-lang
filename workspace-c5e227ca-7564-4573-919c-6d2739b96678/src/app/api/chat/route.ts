// src/app/api/chat/route.ts
// Aviora companion endpoint. Takes the conversation history + a character
// profile, returns { reply, metadata } — where `reply` is the clean spoken
// line and `metadata` is the avatar-sync block parsed out of the LLM output.
//
// POST /api/chat
//   body: { messages: ChatMessage[], character: CharacterProfile }
//   → 200 { reply: string, metadata: AvatarMetadata }
//   | 400 {error} | 502 {error}
//
// The LLM is driven by the Aviora master system prompt composed from the
// character profile, so the same character always sounds like itself across
// turns — the per-turn LOOP reminder is re-interpolated on every call so
// drift can't accumulate.

import { NextRequest, NextResponse } from "next/server";
import ZAI from "z-ai-web-dev-sdk";

import { AVIORA_CHARACTER, assertAdultCharacter } from "@/lib/aviora/character";
import {
  buildAvioraSystemPrompt,
  parseAvioraReply,
} from "@/lib/aviora/system-prompt";
import type {
  AvatarMetadata,
  ChatMessage,
  ChatRequest,
  ChatResponse,
} from "@/lib/aviora/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function isChatMessage(v: unknown): v is ChatMessage {
  if (!v || typeof v !== "object") return false;
  const m = v as Record<string, unknown>;
  return (
    (m.role === "system" || m.role === "user" || m.role === "assistant") &&
    typeof m.content === "string"
  );
}

export async function POST(req: NextRequest) {
  let body: ChatRequest;
  try {
    body = (await req.json()) as ChatRequest;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const character = body?.character ?? AVIORA_CHARACTER;
  try {
    assertAdultCharacter(character);
  } catch (e) {
    return NextResponse.json(
      { error: (e as Error).message },
      { status: 400 }
    );
  }

  const rawMessages = Array.isArray(body?.messages) ? body.messages : [];
  const conversationMessages: ChatMessage[] = rawMessages
    .filter(isChatMessage)
    .slice(-20); // keep last 20 turns to stay inside context window

  if (conversationMessages.length === 0) {
    return NextResponse.json(
      { error: "messages must be a non-empty array of {role, content}" },
      { status: 400 }
    );
  }

  // Build the system prompt with the CURRENT character state — every call
  // re-interpolates the LOOP reminder so the LLM always sees fresh state.
  const systemPrompt = buildAvioraSystemPrompt(character);

  const messagesForLlm = [
    { role: "system" as const, content: systemPrompt },
    ...conversationMessages.map((m) => ({
      role: m.role,
      // Strip any prior metadata out of history — the LLM should only see
      // clean spoken text from previous turns, not the avatar JSON we
      // returned to the client.
      content: m.content,
    })),
  ];

  let zai: Awaited<ReturnType<typeof ZAI.create>>;
  try {
    zai = await ZAI.create();
  } catch (err) {
    console.error("[/api/chat] ZAI.create() failed:", err);
    return NextResponse.json(
      { error: "companion backend unavailable" },
      { status: 502 }
    );
  }

  let raw: string;
  try {
    const completion = await zai.chat.completions.create({
      messages: messagesForLlm,
      // GLM-4.5 reads the system prompt more reliably when thinking is
      // disabled — for short companion replies the cost is latency, not
      // quality.
      thinking: { type: "disabled" },
      temperature: 0.8,
    });
    raw = extractReplyText(completion);
  } catch (err) {
    console.error("[/api/chat] chat.completions.create failed:", err);
    return NextResponse.json(
      { error: "companion reply failed", detail: (err as Error)?.message },
      { status: 502 }
    );
  }

  if (!raw) {
    return NextResponse.json(
      { error: "companion returned an empty reply" },
      { status: 502 }
    );
  }

  const { reply, metadata } = parseAvioraReply(raw, character.current_emotion);

  // Final guard: never ship an empty spoken line — the client can't TTS
  // nothing. Fall back to a soft generic line so the conversation keeps
  // flowing instead of dead-ending.
  const safeReply = reply.trim().length > 0 ? reply.trim() : fallbackLine(character.name);
  const safeMetadata: AvatarMetadata = metadata;

  const response: ChatResponse = { reply: safeReply, metadata: safeMetadata };
  return NextResponse.json(response);
}

function extractReplyText(completion: unknown): string {
  if (!completion || typeof completion !== "object") return "";
  const c = completion as Record<string, unknown>;
  const choices = c.choices as Array<Record<string, unknown>> | undefined;
  if (!Array.isArray(choices) || choices.length === 0) return "";
  const first = choices[0];
  const msg = first?.message as { content?: string } | undefined;
  if (typeof msg?.content === "string") return msg.content;
  // Some SDKs return text directly on the choice
  if (typeof (first as { text?: string }).text === "string") {
    return (first as { text: string }).text;
  }
  return "";
}

function fallbackLine(name: string): string {
  return `Hmm... ${name} here. I'm still listening, even when the words go quiet for a moment.`;
}
