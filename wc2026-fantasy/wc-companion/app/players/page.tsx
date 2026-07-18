import { getSnapshot } from "@/lib/snapshot";
import { PageHeader } from "@/components/widgets";
import { PlayerTable } from "@/components/PlayerTable";

export default function PlayersPage() {
  const snap = getSnapshot();
  return (
    <>
      <PageHeader title="Players" subtitle={`${snap.players.length} players from the official WC2026 pool — engine projections`} />
      <PlayerTable players={snap.players} />
    </>
  );
}
