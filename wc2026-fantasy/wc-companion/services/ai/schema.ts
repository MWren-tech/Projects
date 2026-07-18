import { z } from "zod";

// Structured AI output contract. Used to force tool output and validate it.
export const recommendationSchema = z.object({
  recommendation: z.string().describe("The player or strategy being recommended"),
  confidence: z.enum(["Low", "Medium", "High"]),
  reasoning: z.string().describe("Why the engine + analysis support this"),
  expectedOutcome: z.string().describe("Projected points / value impact"),
  risk: z.enum(["Low", "Medium", "High"]),
  alternatives: z.array(z.string()).describe("1-3 backup options"),
});

export type RecommendationOutput = z.infer<typeof recommendationSchema>;

// JSON schema handed to Claude as a forced tool so output is always structured.
export const recommendationTool = {
  name: "give_recommendation",
  description: "Return a structured fantasy recommendation grounded in the provided data.",
  input_schema: {
    type: "object" as const,
    properties: {
      recommendation: { type: "string" },
      confidence: { type: "string", enum: ["Low", "Medium", "High"] },
      reasoning: { type: "string" },
      expectedOutcome: { type: "string" },
      risk: { type: "string", enum: ["Low", "Medium", "High"] },
      alternatives: { type: "array", items: { type: "string" } },
    },
    required: ["recommendation", "confidence", "reasoning", "expectedOutcome", "risk", "alternatives"],
  },
};
