import type { AIRecommendation } from "@/types";
import { Badge, Card } from "@/components/ui/primitives";
import { riskTone, confidenceTone } from "@/lib/utils";

// Renders the structured AI contract as a premium recommendation card.
export function RecommendationCard({ rec }: { rec: AIRecommendation }) {
  return (
    <Card className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="label">Recommendation</div>
          <div className="mt-0.5 text-lg font-semibold text-fg">{rec.recommendation}</div>
        </div>
        <div className="flex shrink-0 gap-1.5">
          <Badge tone={confidenceTone(rec.confidence) as any}>Confidence: {rec.confidence}</Badge>
          <Badge tone={riskTone(rec.risk) as any}>Risk: {rec.risk}</Badge>
        </div>
      </div>

      <Section label="Reason">{rec.reasoning}</Section>
      <Section label="Expected outcome">{rec.expectedOutcome}</Section>

      {rec.alternatives.length > 0 && (
        <div>
          <div className="label mb-1">Alternatives</div>
          <div className="flex flex-wrap gap-1.5">
            {rec.alternatives.map((a, i) => (
              <Badge key={i} tone="muted">{a}</Badge>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="label mb-0.5">{label}</div>
      <p className="text-sm leading-relaxed text-fg/90">{children}</p>
    </div>
  );
}
