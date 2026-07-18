import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const POS_COLORS: Record<string, string> = {
  GK: "text-gk border-gk/40 bg-gk/10",
  DEF: "text-def border-def/40 bg-def/10",
  MID: "text-mid border-mid/40 bg-mid/10",
  FWD: "text-fwd border-fwd/40 bg-fwd/10",
};

export function money(n: number) {
  return `$${n.toFixed(1)}m`;
}

export function pct(n: number | null | undefined) {
  if (n == null) return "—";
  return `${Math.round(n)}%`;
}

export function ease(label: number | null | undefined) {
  // fixture ease: >1 soft, <1 tough
  if (label == null) return { text: "—", tone: "muted" as const };
  if (label >= 1.25) return { text: "Easy", tone: "accent" as const };
  if (label >= 1.05) return { text: "Favourable", tone: "info" as const };
  if (label >= 0.95) return { text: "Neutral", tone: "muted" as const };
  if (label >= 0.85) return { text: "Tough", tone: "warn" as const };
  return { text: "Very tough", tone: "danger" as const };
}

export function riskTone(risk: string) {
  // Low risk = good (green), High risk = bad (red).
  return risk === "Low" ? "accent" : risk === "Medium" ? "warn" : "danger";
}

export function confidenceTone(confidence: string) {
  // High confidence = good (green), Low confidence = caution (red).
  return confidence === "High" ? "accent" : confidence === "Medium" ? "warn" : "danger";
}
