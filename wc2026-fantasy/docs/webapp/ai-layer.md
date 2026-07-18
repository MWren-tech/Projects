# AI layer (in-app Claude)

Located in `wc-companion/services/ai/`. Powers the chat and structured recommendations.

## Principle: grounded, never inventive
Claude only ever references players from the **snapshot's player list**, injected into the prompt. It explains/arranges the model's numbers; it does not produce new numbers or invent players (we fought hallucinated players earlier — this is non-negotiable).

## Files
- `client.ts` — Anthropic SDK client; `isAIConfigured()` (graceful degrade if no key). Model from `ANTHROPIC_MODEL`.
- `prompts.ts` — `SYSTEM_PROMPT` (persona + hard grounding rules) + `buildContext()` which injects a **token-bounded** relevant slice: rules, booster schedule, the user's squad, and a shortlist (top players + anyone named in the question) + fixtures.
- `schema.ts` — zod schema + forced-tool definition so structured answers always match `{ recommendation, confidence, reasoning, expectedOutcome, risk, alternatives }`.
- `assistant.ts` — `getStructuredRecommendation()` (forced tool) and `streamChat()` (streaming text).

## API routes
- `POST /api/chat` — streams a grounded answer (falls back to a friendly notice if no API key).
- `POST /api/recommend` — returns the structured contract; persisted to `AIRecommendation`.

## Cost & keys
- Needs `ANTHROPIC_API_KEY` in `.env.local` (**pay-as-you-go, not Claude Pro**). Everything else in the app works without it — only free-text chat is disabled.
- Keep prompts token-bounded; cache staple answers where possible.

## Rules for changes
- Keep the grounding constraints in `SYSTEM_PROMPT`.
- If the snapshot adds fields useful to the AI, surface them in `buildContext()` deliberately (don't dump the whole snapshot).
