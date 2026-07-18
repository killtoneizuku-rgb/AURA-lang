// src/app/page.tsx
// Aviora companion experience — full-screen chat with avatar + voice.

import { CompanionChat } from "@/components/aviora/companion-chat";
import { AVIORA_CHARACTER } from "@/lib/aviora/character";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-violet-50">
      {/* Top bar */}
      <header className="sticky top-0 z-10 border-b border-rose-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-rose-400 to-violet-400 text-white shadow-[0_4px_12px_rgba(217,140,166,0.4)]">
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden="true">
                <path d="M12 2l1.8 4.5L18 8l-4.2 1.5L12 14l-1.8-4.5L6 8l4.2-1.5L12 2z" />
                <path d="M19 14l.9 2.2L22 17l-2.1.8L19 20l-.9-2.2L16 17l2.1-.8L19 14z" opacity="0.7" />
              </svg>
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight text-rose-950">
                Aviora
              </h1>
              <p className="text-[11px] text-rose-400">
                AI companion · voice + avatar
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-3 text-xs text-rose-400 sm:flex">
            <span className="rounded-full bg-rose-50 px-3 py-1">
              {AVIORA_CHARACTER.relationship_level}
            </span>
            <span className="rounded-full bg-rose-50 px-3 py-1">
              {AVIORA_CHARACTER.world_setting.split(",")[0]}
            </span>
          </div>
        </div>
      </header>

      {/* Chat surface */}
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
        <CompanionChat character={AVIORA_CHARACTER} />
      </div>

      {/* Footer */}
      <footer className="mt-8 border-t border-rose-100 bg-white/60 py-4">
        <div className="mx-auto max-w-6xl px-6 text-center text-[11px] text-rose-400">
          Aviora is an AI companion — every character is 18+. If you're in a real
          crisis, please reach out to a person you trust or a local crisis line.
        </div>
      </footer>
    </main>
  );
}
