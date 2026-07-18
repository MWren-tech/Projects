import { PrismaClient } from "@prisma/client";

// Single Prisma instance across hot reloads in dev.
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

export const DEFAULT_USER_ID = process.env.DEFAULT_USER_ID ?? "local-user";

// Ensures the single local user row exists (no auth in the MVP).
export async function ensureLocalUser() {
  await prisma.user.upsert({
    where: { id: DEFAULT_USER_ID },
    update: {},
    create: { id: DEFAULT_USER_ID, name: "You" },
  });
  return DEFAULT_USER_ID;
}
