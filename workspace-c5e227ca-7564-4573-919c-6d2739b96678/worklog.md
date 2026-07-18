---
Task ID: aviora-1
Agent: main
Task: Build the complete Aviora AI companion app — character engine, TTS backend, voice hook, and chat UI — based on the user-provided master system prompt + server-tts.js + useVoiceSynthesis.js + VoicePlayerExample.jsx.

Work Log:
- Initialized the Next.js 16 fullstack project (skill: fullstack-dev).
- Installed msedge-tts@2.0.7 (same package the user's spec used).
- Smoke-tested both TTS providers in the sandbox: msedge-tts OK (21KB MP3), z-ai-web-dev-sdk audio.tts blocked by response_format quirk — kept msedge-tts as primary since it matched the spec exactly.
- Built the Aviora character engine under `src/lib/aviora/`:
  - `types.ts` — Emotion, RelationshipLevel, CharacterProfile, AvatarMetadata, ChatMessage, ChatRequest/Response, TtsRequest.
  - `character.ts` — default Aviora character (22 y/o spirit of the quiet hour), voice picker shortlist, age-gate helper.
  - `emotion-presets.ts` — emotion → prosody map + avatar baseline poses (one tag drives both face and voice).
  - `system-prompt.ts` — builds the master Aviora prompt dynamically from any CharacterProfile, with per-turn LOOP reminder interpolation; also parses the LLM's reply into a clean spoken line + avatar metadata block.
- Built the TTS API at `src/app/api/tts/route.ts` (TypeScript port of server-tts.js, adapted to Next.js App Router). Includes SSML escaping, emotion-driven prosody presets, server-side msedge-tts synthesis, and proper WebSocket cleanup on every request.
- Built `src/app/api/tts/voices/route.ts` — exposes the live Microsoft voice catalog (322 voices) with 1-hour in-process cache.
- Built the chat endpoint at `src/app/api/chat/route.ts` — composes the system prompt, calls z-ai-web-dev-sdk chat.completions, parses reply + metadata, validates character is 18+.
- Built `src/hooks/use-voice-synthesis.ts` — TypeScript port of useVoiceSynthesis.js with browser SpeechSynthesis fallback. Added autoplay-blocked handling: if the browser refuses play() before first user interaction, queue the audio to resume on the next click/keydown/touchstart.
- Built UI components under `src/components/aviora/`:
  - `avatar-portrait.tsx` — pure-CSS avatar whose pose (expression, eye movement, head tilt, blink rate, smile intensity, mood aura) is driven by AvatarMetadata via Framer Motion.
  - `voice-player.tsx` — shadcn/ui Button-based rewrite of VoicePlayerExample.jsx with mute/replay/loading states.
  - `message-bubble.tsx` — chat bubble with avatar portrait + emotion chip + voice controls on the latest assistant turn.
  - `companion-chat.tsx` — full chat surface: header with voice status, scrollable history, composer with Enter-to-send, side panel with live avatar + voice picker + character bio.
- Updated `src/app/page.tsx` to render the full Aviora experience with header/footer/safety note.
- Updated `src/app/layout.tsx` metadata to reflect the Aviora brand.
- Lint: clean (0 errors, 0 warnings).
- Smoke tests: all 4 emotions produce valid MP3 audio of distinct byte sizes; /api/chat returns well-formed {reply, metadata}; /api/tts/voices returns 322 voices.
- Agent Browser self-verification: page renders cleanly, sending a message returns a perfectly in-character reply with the correct emotional detection (anxious user → "comforting" emotion), avatar pose updates to match (soft smile / gentle gaze / slight tilt / leaning in / slow blink), voice plays successfully after the first user interaction, zero console errors, zero page errors. Mobile (390×844) and desktop (1280×800) layouts both render correctly.

Stage Summary:
- Deliverable: a complete, voice-first AI companion app at the / route, with character engine + LLM chat + TTS + avatar sync all wired end-to-end.
- Files created:
  - src/lib/aviora/{types,character,emotion-presets,system-prompt}.ts
  - src/app/api/tts/route.ts, src/app/api/tts/voices/route.ts, src/app/api/chat/route.ts
  - src/hooks/use-voice-synthesis.ts
  - src/components/aviora/{avatar-portrait,voice-player,message-bubble,companion-chat}.tsx
  - src/app/page.tsx (updated), src/app/layout.tsx (metadata updated)
  - scripts/{test-tts,test-tts-emotions,test-chat}.mjs for future verification
- Deviations from user's original spec, all justified:
  - server-tts.js ported to TypeScript App Router (src/app/api/tts/route.ts) — required by Next.js 16.
  - useVoiceSynthesis.js ported to TypeScript and given autoplay-blocked handling — required by modern browser autoplay policies.
  - Added /api/chat endpoint using z-ai-web-dev-sdk so the companion actually responds — the user provided the character engine prompt but no chat backend, so the app would have been static without this.
  - VoicePlayerExample.jsx rewritten as VoicePlayer + MessageBubble + CompanionChat for a complete chat experience rather than a single demo bubble.
