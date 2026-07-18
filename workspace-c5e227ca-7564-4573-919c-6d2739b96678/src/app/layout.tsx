import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Aviora — AI Companion",
  description:
    "Aviora is a premium AI anime companion platform — voice-first conversation with an expressive avatar driven by a character engine.",
  keywords: ["Aviora", "AI companion", "voice", "TTS", "character engine"],
  authors: [{ name: "ar0x" }],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "Aviora — AI Companion",
    description: "Voice-first conversation with an expressive AI companion.",
    siteName: "Aviora",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Aviora — AI Companion",
    description: "Voice-first conversation with an expressive AI companion.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
