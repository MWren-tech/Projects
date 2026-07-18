import { getSnapshot } from "@/lib/snapshot";
import { PageHeader } from "@/components/widgets";
import { CompareTool } from "@/components/CompareTool";

export default function ComparePage() {
  const snap = getSnapshot();
  return (
    <>
      <PageHeader title="Compare Players" subtitle="Head-to-head on the metrics that decide fantasy points" />
      <CompareTool players={snap.players} />
    </>
  );
}
