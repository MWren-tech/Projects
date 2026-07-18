import { defineConfig } from "vitest/config";

// Pure-logic unit tests (engine math). Node environment — no DOM needed.
export default defineConfig({
  test: {
    environment: "node",
    include: ["lib/**/*.test.ts"],
  },
});
