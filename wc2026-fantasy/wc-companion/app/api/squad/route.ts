import { NextRequest, NextResponse } from "next/server";
import { prisma, ensureLocalUser } from "@/lib/db";

export const runtime = "nodejs";

// Load the active squad's player ids.
export async function GET() {
  const userId = await ensureLocalUser();
  const squad = await prisma.squad.findFirst({
    where: { userId, isActive: true },
    include: { players: true },
    orderBy: { updatedAt: "desc" },
  });
  return NextResponse.json({
    squadId: squad?.id ?? null,
    playerIds: squad?.players.map((p) => p.playerId) ?? [],
  });
}

// Save / replace the active squad (player ids from the snapshot).
export async function POST(req: NextRequest) {
  const { playerIds, name = "My Squad", formation = "3-4-3" } = await req.json();
  const userId = await ensureLocalUser();

  const squad = await prisma.squad.upsert({
    where: { id: (await activeSquadId(userId)) ?? "___none___" },
    update: { name, formation, updatedAt: new Date() },
    create: { userId, name, formation, isActive: true },
  });

  await prisma.squadPlayer.deleteMany({ where: { squadId: squad.id } });
  await prisma.squadPlayer.createMany({
    data: (playerIds as string[]).map((playerId) => ({ squadId: squad.id, playerId })),
  });
  return NextResponse.json({ squadId: squad.id, count: playerIds.length });
}

async function activeSquadId(userId: string): Promise<string | null> {
  const s = await prisma.squad.findFirst({ where: { userId, isActive: true } });
  return s?.id ?? null;
}
