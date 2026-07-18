import type { Player, Snapshot, AIRecommendation } from "@/types";
import { getClient, AI_MODEL } from "./client";
import { SYSTEM_PROMPT, buildContext } from "./prompts";
import { recommendationTool, recommendationSchema } from "./schema";

// Structured recommendation: forces Claude to return the JSON contract via a tool.
export async function getStructuredRecommendation(
  snapshot: Snapshot,
  question: string,
  squad: Player[] = []
): Promise<AIRecommendation> {
  const client = getClient();
  const msg = await client.messages.create({
    model: AI_MODEL,
    max_tokens: 1024,
    system: SYSTEM_PROMPT,
    tools: [recommendationTool] as any,
    tool_choice: { type: "tool", name: recommendationTool.name },
    messages: [{ role: "user", content: buildContext(snapshot, question, squad) }],
  });
  const block = msg.content.find((b) => b.type === "tool_use");
  if (!block || block.type !== "tool_use") throw new Error("No structured output returned.");
  return recommendationSchema.parse(block.input) as AIRecommendation;
}

// Streaming free-text chat (returns a web ReadableStream of text chunks).
export function streamChat(
  snapshot: Snapshot,
  question: string,
  squad: Player[] = [],
  history: { role: "user" | "assistant"; content: string }[] = []
): ReadableStream<Uint8Array> {
  const client = getClient();
  const encoder = new TextEncoder();

  return new ReadableStream({
    async start(controller) {
      try {
        const stream = client.messages.stream({
          model: AI_MODEL,
          max_tokens: 1200,
          system:
            SYSTEM_PROMPT +
            "\n\nFormat answers with these bold labels when giving a pick: **Recommendation**, **Reason**, **Expected outcome**, **Risk** (Low/Medium/High), **Alternative**.",
          messages: [
            ...history,
            { role: "user", content: buildContext(snapshot, question, squad) },
          ],
        });
        for await (const event of stream) {
          if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
            controller.enqueue(encoder.encode(event.delta.text));
          }
        }
        controller.close();
      } catch (err) {
        controller.enqueue(
          encoder.encode(`\n\n[AI error: ${(err as Error).message}]`)
        );
        controller.close();
      }
    },
  });
}
