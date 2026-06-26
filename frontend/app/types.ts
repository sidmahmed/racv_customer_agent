export type ChatRequest = {
  session_id: string;
  message: string;
};

export type ChatResponse = {
  session_id: string;
  response: string;
};

export type ChatStreamChunk = {
  content: string;
};

export type ChatMessage = {
  role: string;
  content: string;
};

export type ChatHistoryResponse = {
  session_id: string;
  messages: ChatMessage[];
};
