import { getSnapshot } from "@/lib/snapshot";
import { PageHeader } from "@/components/widgets";
import { Card, CardTitle, Badge } from "@/components/ui/primitives";

const DESC: Record<string, string> = {
  Wildcard: "Unlimited transfers for one round (not MD1 or R32).",
  "12th Man": "A 13th player scores for one round — any player, no budget or nation cap.",
  "Maximum Captain": "Doubles whichever starter scores most that round (auto-captain).",
  Qualification: "R32+: +2 per starter who advances to the next round.",
  Mystery: "Revealed at R32 — used once in a knockout round.",
};

export default function BoostsPage() {
  const snap = getSnapshot();
  const { schedule, perRound } = snap.boosterPlan;

  return (
    <>
      <PageHeader title="Boost Strategy" subtitle="When to play each one-time booster — engine EV by round" />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(schedule).map(([chip, s]) => (
          <Card key={chip}>
            <div className="flex items-start justify-between">
              <div>
                <div className="font-semibold text-fg">{chip}</div>
                <p className="mt-1 text-xs text-muted">{DESC[chip]}</p>
              </div>
              <Badge tone="accent">{s.round}</Badge>
            </div>
            {s.ev != null ? (
              <div className="mt-3 text-xs text-muted">Expected value: <span className="num font-semibold text-accent">+{s.ev} pts</span></div>
            ) : (
              <div className="mt-3 text-xs text-muted">Timing is structural (see notes).</div>
            )}
          </Card>
        ))}
      </div>

      <Card className="mt-4">
        <CardTitle hint="higher = better that round">Expected value by round</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="px-3 py-2">Round</th>
                <th className="px-3 text-right">Maximum Captain</th>
                <th className="px-3">12th Man (best pick)</th>
                <th className="px-3 text-right">Qualification</th>
              </tr>
            </thead>
            <tbody>
              {perRound.map((r) => (
                <tr key={r.round} className="border-b border-border/50">
                  <td className="px-3 py-2 font-medium text-fg">{r.round}</td>
                  <td className="num px-3 text-right text-accent">+{r.maxCaptain.toFixed(2)}</td>
                  <td className="px-3 text-muted">
                    {r.twelfthMan ? <span><span className="text-fg">{r.twelfthMan.name}</span> ({r.twelfthMan.nation}) <span className="num text-accent">+{r.twelfthMan.ev}</span></span> : "—"}
                  </td>
                  <td className="num px-3 text-right text-info">{r.qualification != null ? `+${r.qualification.toFixed(1)}` : "n/a"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-muted">
          Group-round numbers use real fixture ease; knockout numbers are team-strength proxies (bracket undrawn). Re-run{" "}
          <code className="text-accent">npm run snapshot</code> after each round once draws are made.
        </p>
      </Card>
    </>
  );
}
