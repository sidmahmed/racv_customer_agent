"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { streamChat } from "./stream";

type Message = {
  role: "user" | "assistant";
  content: string;
};

// Defaults to same-origin ("") so production (one Vercel project routing
// /api/* to the backend service) needs no env var at all. Local dev sets
// NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local since the two
// dev servers run on different ports.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

// Real "Top questions" pulled verbatim from each RACV Help & Support page.
const EXAMPLE_QUESTIONS = [
  "How soon can I use RACV Emergency Roadside Assistance?",
  "How do I update my car insurance policy?",
  "How do I become an RACV Member?",
];

function getSessionId(): string {
  const key = "chat-session-id";
  let sessionId = localStorage.getItem(key);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(key, sessionId);
  }
  return sessionId;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  function appendToLastMessage(text: string) {
    setMessages((prev) => {
      const next = [...prev];
      const last = next[next.length - 1];
      next[next.length - 1] = { ...last, content: last.content + text };
      return next;
    });
  }

  async function sendMessage(override?: string) {
    const text = (override ?? input).trim();
    if (!text || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ]);
    setInput("");
    setLoading(true);

    try {
      for await (const chunk of streamChat(API_URL, {
        session_id: getSessionId(),
        message: text,
      })) {
        appendToLastMessage(chunk);
      }
    } catch {
      appendToLastMessage("Something went wrong. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col bg-surface">
      <header className="shrink-0 bg-primary px-4 py-10 sm:px-10">
        <div className="mx-auto w-full max-w-2xl">
          <h1
            className="font-sans text-[28px] leading-[1.1] font-normal text-neutral"
            style={{ fontFamily: "var(--font-poppins)" }}
          >
            RACV Help Assistant
          </h1>
          <p className="mt-2 font-body text-[16px] leading-[30px] text-neutral/80">
            Ask about roadside assistance, car or home insurance, billing, and more.
          </p>
        </div>
      </header>

      <main className="mx-auto -mt-6 flex w-full min-h-0 max-w-2xl flex-1 flex-col gap-4 px-4 pb-10 sm:px-10">
        <div
          ref={scrollRef}
          className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto rounded-md border border-border bg-card p-4 shadow-sm"
        >
          {messages.length === 0 && (
            <p className="font-body text-sm text-muted">Send a message to get started.</p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[80%] rounded-md px-3 py-2 font-body text-sm ${
                m.role === "user" ? "self-end bg-primary text-neutral" : "self-start bg-surface text-on-surface"
              }`}
            >
              {m.role === "assistant" ? (
                m.content ? (
                  <div className="prose prose-sm max-w-none prose-a:text-primary [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                ) : (
                  <span className="text-muted">Thinking…</span>
                )
              ) : (
                m.content
              )}
            </div>
          ))}
        </div>

        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
        >
          <input
            className="flex-1 rounded-sm border border-border bg-neutral px-4 py-[14px] font-body text-sm text-on-surface outline-none focus:border-primary"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about RACV..."
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-full bg-tertiary px-[22px] py-[14px] font-sans text-[16px] font-medium text-secondary disabled:opacity-50"
          >
            Send
          </button>
        </form>

        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUESTIONS.map((question) => (
            <button
              key={question}
              type="button"
              disabled={loading}
              onClick={() => sendMessage(question)}
              className="rounded-full border border-border bg-card px-3 py-2 font-body text-sm text-secondary hover:bg-surface disabled:opacity-50"
            >
              {question}
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
