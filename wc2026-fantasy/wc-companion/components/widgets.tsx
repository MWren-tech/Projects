import { cn, POS_COLORS, ease } from "@/lib/utils";
import { Badge } from "@/components/ui/primitives";

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-fg">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-muted">{subtitle}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function PosBadge({ pos }: { pos: string }) {
  return (
    <span className={cn("chip border font-semibold", POS_COLORS[pos])}>{pos}</span>
  );
}

export function EaseBadge({ value }: { value: number | null | undefined }) {
  const e = ease(value);
  return <Badge tone={e.tone}>{e.text}</Badge>;
}

// A compact circular gauge for an AI rating / score (0-100).
export function RatingDial({ value, size = 56, label }: { value: number; size?: number; label?: string }) {
  const r = (size - 8) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - Math.max(0, Math.min(100, value)) / 100);
  const tone = value >= 75 ? "#3ee6a0" : value >= 50 ? "#5aa9ff" : value >= 30 ? "#ffb454" : "#ff5d6c";
  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#252b36" strokeWidth={5} fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={r} stroke={tone} strokeWidth={5} fill="none"
          strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round"
        />
      </svg>
      <div className="absolute text-center">
        <div className="num text-sm font-bold text-fg">{Math.round(value)}</div>
        {label ? <div className="text-[8px] uppercase text-muted">{label}</div> : null}
      </div>
    </div>
  );
}

// Mini horizontal bar for a stat against a sensible max.
export function StatBar({ label, value, max, suffix }: { label: string; value: number; max: number; suffix?: string }) {
  const w = Math.max(2, Math.min(100, (value / max) * 100));
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted">{label}</span>
        <span className="num text-fg">{value}{suffix}</span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-surface-2">
        <div className="h-full rounded-full bg-accent/80" style={{ width: `${w}%` }} />
      </div>
    </div>
  );
}
