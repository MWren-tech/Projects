# Deploying the companion (Vercel)

The web app is a Next.js app with server components and API routes, so it needs a Node
host — **Vercel** (free tier is plenty). GitHub Pages won't work: it only serves static
files, and this app renders on the server, reads `snapshot.json` from disk at runtime and
exposes API routes.

**The Python model does not deploy.** `wc_scout/` runs locally (or on a schedule) to
produce `wc-companion/data/snapshot.json`, which is committed to the repo. The deployed
app just serves that snapshot — so the live site needs no API-Football key and no Python.

---

## Import the repo (one time)

1. On [vercel.com](https://vercel.com) → **Add New → Project** → import the GitHub repo
   (`MWren-tech/Projects`).
2. **Root Directory: `wc2026-fantasy/wc-companion`** — this is the critical step; the app
   is a subfolder of a portfolio monorepo, not the repo root.
3. Framework preset **Next.js** is auto-detected; leave the build/install commands default.
4. Add the environment variables below, then **Deploy**.

`prisma generate` runs automatically on install (via the `postinstall` script), and
`next.config.mjs` already forces `data/snapshot.json` into each serverless function bundle.

---

## Environment variables

| Variable | Tier 1 — read-only demo | Tier 2 — full persistence |
|---|---|---|
| `DATABASE_URL` | `file:/tmp/dev.db` (dummy) | your Postgres connection string |
| `ANTHROPIC_API_KEY` | *(optional — enables AI chat)* | same |
| `DEFAULT_USER_ID` | `local-user` | `local-user` |

### Tier 1 — read-only demo (fastest, no database)

Everything a visitor sees renders from the bundled `snapshot.json`: dashboard, the full
player pool, the squad builder (its state lives in the browser's localStorage), transfer
planner, boost strategy and compare. The **only** inert features are "save squad to your
account" and AI-recommendation history — both need a real database. Add `ANTHROPIC_API_KEY`
and the chat works too.

Set `DATABASE_URL=file:/tmp/dev.db` (a dummy value so Prisma can initialise) and deploy.
Nothing writes to it in normal browsing.

### Tier 2 — full persistence (saved squads, history)

1. Create a Postgres database — **Vercel → Storage → Postgres**, or a free
   [Neon](https://neon.tech) database.
2. In `wc-companion/prisma/schema.prisma`, change the datasource `provider` from
   `"sqlite"` to `"postgresql"` (the models are portable).
3. Set `DATABASE_URL` to the Postgres connection string.
4. Set the Vercel **Build Command** to create the schema and seed it on deploy:
   ```
   prisma db push && npm run db:seed && next build
   ```

---

## After it's live

- Put the deployment URL at the top of [README.md](README.md) (replace the *Live demo*
  placeholder).
- **Refresh the numbers:** re-run the engine locally
  (`python wc_scout/export_snapshot.py --incremental`), commit the updated
  `wc-companion/data/snapshot.json`, and Vercel redeploys automatically.

## Troubleshooting

- **`snapshot.json not found` (500):** the file wasn't traced into the function — confirm
  Root Directory is `wc2026-fantasy/wc-companion` and that `next.config.mjs` still has the
  `outputFileTracingIncludes` entry.
- **Build fails on Prisma:** ensure the `postinstall: prisma generate` script is present
  (it is) so the client is generated on Vercel's fresh install.
