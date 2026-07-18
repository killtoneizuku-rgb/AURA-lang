// Smoke test for the /api/chat endpoint.
// Run: node /home/z/my-project/scripts/test-chat.mjs

const res = await fetch("http://localhost:3000/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [
      {
        role: "user",
        content: "Hey Aviora, I've had kind of a long day. What do you do when you're tired?",
      },
    ],
    character: {
      name: "Aviora",
      age: 22,
      appearance: "Soft pink hair, amber eyes",
      personality: "Warm, curious, gently playful",
      backstory: "Spirit of the quiet hour",
      speaking_style: "Soft, rhythmic, 1-4 short sentences",
      likes: ["quiet evenings", "warm tea", "stargazing"],
      dislikes: ["rushed conversations"],
      relationship_level: "acquaintance",
      current_mood: "calm and curious",
      current_emotion: "happy",
      voice_style: "Soft warm feminine",
      world_setting: "Cozy apartment at dusk",
      memories: [],
      voice_id: "en-US-JennyNeural",
    },
  }),
});

console.log("status:", res.status);
const text = await res.text();
console.log("raw response:");
console.log(text.slice(0, 1200));
try {
  const json = JSON.parse(text);
  console.log("\nparsed:", JSON.stringify(json, null, 2));
} catch {
  console.log("\n(could not parse as JSON)");
}
