import { getSnapshot } from "@/lib/snapshot";
import { PageHeader } from "@/components/widgets";
import { TransferPlanner } from "@/components/TransferPlanner";

export default function TransfersPage() {
  const snap = getSnapshot();
  return (
    <>
      <PageHeader
        title="Transfer Planner"
        subtitle={`${snap.meta.currentRound} · 2 free transfers · −${snap.rules.transfers.hitCost} pts per extra`}
      />
      <TransferPlanner players={snap.players} />
    </>
  );
}
