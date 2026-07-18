// Quick smoke test for both TTS providers in this sandbox.
// Run: node /home/z/my-project/scripts/test-tts.mjs

import { MsEdgeTTS, OUTPUT_FORMAT } from "msedge-tts";
import { writeFile } from "node:fs/promises";
import ZAI from "z-ai-web-dev-sdk";

const OUT_DIR = "/home/z/my-project/scripts";

async function testEdgeTts() {
  console.log("\n[1/2] Testing msedge-tts...");
  try {
    const tts = new MsEdgeTTS();
    await tts.setMetadata(
      "en-US-JennyNeural",
      OUTPUT_FORMAT.AUDIO_24KHZ_48KBITRATE_MONO_MP3
    );
    const { audioStream } = tts.toStream("Hello there. This is a test.", {
      rate: "+0%",
      pitch: "+0Hz",
    });
    const chunks = [];
    for await (const chunk of audioStream) chunks.push(chunk);
    const buf = Buffer.concat(chunks);
    await writeFile(`${OUT_DIR}/edge-test.mp3`, buf);
    console.log(
      `[msedge-tts] OK — ${buf.length} bytes written to ${OUT_DIR}/edge-test.mp3`
    );
    return true;
  } catch (err) {
    console.error("[msedge-tts] FAILED:", err?.message || err);
    return false;
  }
}

async function testZaiTts() {
  console.log("\n[2/2] Testing z-ai-web-dev-sdk audio.tts.create...");
  try {
    const zai = await ZAI.create();
    const res = await zai.audio.tts.create({
      input: "Hello there. This is a test.",
      voice: "English-expressive-Boy",
      response_format: "mp3",
    });
    console.log("[z-ai-tts] raw response type:", typeof res);
    if (res && typeof res === "object") {
      const keys = Object.keys(res);
      console.log("[z-ai-tts] top-level keys:", keys);
      if (Buffer.isBuffer(res)) {
        await writeFile(`${OUT_DIR}/zai-test.mp3`, res);
        console.log(
          `[z-ai-tts] OK — buffer ${res.length} bytes written to ${OUT_DIR}/zai-test.mp3`
        );
        return true;
      }
      // Try common shapes
      const candidates = [
        res.data,
        res.audio,
        res.buffer,
        res.body,
        res.result,
      ];
      for (const c of candidates) {
        if (Buffer.isBuffer(c)) {
          await writeFile(`${OUT_DIR}/zai-test.mp3`, c);
          console.log(
            `[z-ai-tts] OK — buffer ${c.length} bytes from res.<key> written`
          );
          return true;
        }
      }
      console.error("[z-ai-tts] could not find a Buffer in response shape");
      console.error("[z-ai-tts] sample:", JSON.stringify(res).slice(0, 300));
      return false;
    }
    console.error("[z-ai-tts] unexpected response");
    return false;
  } catch (err) {
    console.error("[z-ai-tts] FAILED:", err?.message || err);
    return false;
  }
}

const edgeOk = await testEdgeTts();
const zaiOk = await testZaiTts();

console.log("\n=== SUMMARY ===");
console.log("msedge-tts:", edgeOk ? "OK" : "FAILED");
console.log("z-ai-web-dev-sdk audio.tts:", zaiOk ? "OK" : "FAILED");
process.exit(0);
