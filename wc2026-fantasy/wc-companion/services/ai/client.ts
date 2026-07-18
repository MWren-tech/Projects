import Anthropic from "@anthropic-ai/sdk";

export const AI_MODEL = process.env.ANTHROPIC_MODEL ?? "claude-opus-4-8";

export function isAIConfigured(): boolean {
  return Boolean(process.env.ANTHROPIC_API_KEY);
}

let client: Anthropic | null = null;

export function getClient(): Anthropic {
  if (!isAIConfigured()) {
    throw new Error(
      "ANTHROPIC_API_KEY is not set. Add it to .env.local to enable the AI chat."
    );
  }
  if (!client) client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  return client;
}
