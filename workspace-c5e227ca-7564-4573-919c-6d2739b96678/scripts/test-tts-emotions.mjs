// Smoke test for /api/tts with different emotions.
// Run: node /home/z/my-project/scripts/test-tts-emotions.mjs

import { writeFile } from "node:fs/promises";

const cases = [
  { emotion: "neutral", text: "Hi there. I'm glad you stopped by tonight." },
  { emotion: "happy", text: "Oh, that's wonderful! Tell me more about it." },
  { emotion: "comforting", text: "It's okay. I'm right here. Take your time." },
  { emotion: "shy", text: "Ehehe... you noticed that about me?" },
];

for (const c of cases) {
  const res = await fetch("http://localhost:3000/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: c.text,
      emotion: c.emotion,
      voiceId: "en-US-JennyNeural",
    }),
  });
  const buf = Buffer.from(await res.arrayBuffer());
  const path = `/home/z/my-project/scripts/tts-${c.emotion}.mp3`;
  await writeFile(path, buf);
  console.log(
    `${c.emotion.padEnd(12)} → status=${res.status}  bytes=${String(buf.length).padStart(6)}  file=${path}`
  );
}

// Also test the voices list endpoint
const vRes = await fetch("http://localhost:3000/api/tts/voices");
console.log("\nGET /api/tts/voices →", vRes.status);
if (vRes.ok) {
  const v = await vRes.json();
  console.log("voices count:", Array.isArray(v.voices) ? v.voices.length : "n/a");
  if (Array.isArray(v.voices)) {
    const en = v.voices.filter((x) => x.ShortName?.startsWith("en-US"));
    console.log("en-US voices sample:", en.slice(0, 5).map((x) => x.ShortName));
  }
}
