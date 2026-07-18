import { getSnapshot } from "@/lib/snapshot";
import { PageHeader } from "@/components/widgets";
import { SquadBuilder } from "@/components/SquadBuilder";

export default function SquadPage() {
  const snap = getSnapshot();
  const optimalSquadIds = [
    ...snap.optimalSquad.xi.map((p) => p.id),
    ...snap.optimalSquad.bench.map((p) => p.id),
  ];
  return (
    <>
      <PageHeader title="Squad Builder" subtitle="Pick 15 — 2 GK · 5 DEF · 5 MID · 3 FWD · $100m · max 3 per nation" />
      <SquadBuilder
        players={snap.players}
        optimalProjected={snap.optimalSquad.projectedPoints}
        optimalSquadIds={optimalSquadIds}
        fixtures={snap.fixtures}
      />
    </>
  );
}
