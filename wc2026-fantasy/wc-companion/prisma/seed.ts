import { PrismaClient } from "@prisma/client";
import fs from "fs";
import path from "path";

// Load .env manually — the Prisma CLI normally does this, but when we run the seed
// directly via tsx it doesn't, so DATABASE_URL would be missing.
try {
  for (const line of fs.readFileSync(path.join(process.cwd(), ".env"), "utf-8").split("\n")) {
    const m = line.match(/^\s*([A-Z_]+)\s*=\s*"?([^"\n]*)"?\s*$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
} catch {}

const prisma = new PrismaClient();

// Seeds the DB from the engine snapshot so squad/watchlist references resolve.
// Re-run after each `npm run snapshot` to keep prices/projections in sync.
async function main() {
  const file = path.join(process.cwd(), "data", "snapshot.json");
  if (!fs.existsSync(file)) {
    throw new Error("data/snapshot.json missing — run `npm run snapshot` first.");
  }
  const snap = JSON.parse(fs.readFileSync(file, "utf-8"));

  await prisma.user.upsert({
    where: { id: process.env.DEFAULT_USER_ID ?? "local-user" },
    update: {},
    create: { id: process.env.DEFAULT_USER_ID ?? "local-user", name: "You" },
  });

  for (const p of snap.players) {
    await prisma.player.upsert({
      where: { id: p.id },
      update: {
        name: p.name, nation: p.nation, club: p.club, pos: p.pos, price: p.price,
        xp: p.xp, ownership: p.ownership, value: p.value, goals: p.goals, assists: p.assists,
        g90: p.g90, a90: p.a90, cleanSheet: p.cleanSheet, fixtureEase: p.fixtureEase,
        setPieces: p.setPieces, rating: p.rating, startProb: p.startProb,
        aiRating: p.aiRating, differential: p.differential, updatedAt: new Date(),
      },
      create: {
        id: p.id, name: p.name, nation: p.nation, club: p.club, pos: p.pos, price: p.price,
        xp: p.xp, ownership: p.ownership, value: p.value, goals: p.goals, assists: p.assists,
        g90: p.g90, a90: p.a90, cleanSheet: p.cleanSheet, fixtureEase: p.fixtureEase,
        setPieces: p.setPieces, rating: p.rating, startProb: p.startProb,
        aiRating: p.aiRating, differential: p.differential,
      },
    });
  }

  for (const [nation, f] of Object.entries<any>(snap.fixtures)) {
    await prisma.fixture.upsert({
      where: { nation_round: { nation, round: snap.meta.currentRound } },
      update: { opponent: f.nextOpponent, fixtureEase: f.fixtureEase, cleanSheet: f.cleanSheet },
      create: { nation, round: snap.meta.currentRound, opponent: f.nextOpponent, fixtureEase: f.fixtureEase, cleanSheet: f.cleanSheet },
    });
  }

  console.log(`Seeded ${snap.players.length} players + fixtures.`);
}

main().finally(() => prisma.$disconnect());
