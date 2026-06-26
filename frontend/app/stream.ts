import type { ChatRequest, ChatStreamChunk } from "./types";

export async function* streamChat(
  apiUrl: string,
  request: ChatRequest,
): AsyncGenerator<string> {
  const res = await fetch(`${apiUrl}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok || !res.body) {
    throw new Error(`Request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data:"));
      if (!dataLine) continue;
      const json = dataLine.slice("data:".length).trim();
      if (!json) continue;
      const chunk = JSON.parse(json) as ChatStreamChunk;
      if (chunk.content) yield chunk.content;
    }
  }
}
