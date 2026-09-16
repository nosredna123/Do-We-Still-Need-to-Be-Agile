export const MessageRole = {
  User: "U",
  Assistant: "A",
} as const;

export type MessageRole = (typeof MessageRole)[keyof typeof MessageRole];
