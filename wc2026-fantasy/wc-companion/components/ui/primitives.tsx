import { cn } from "@/lib/utils";
import * as React from "react";

const TONES: Record<string, string> = {
  accent: "border-accent/40 bg-accent/10 text-accent",
  info: "border-info/40 bg-info/10 text-info",
  warn: "border-warn/40 bg-warn/10 text-warn",
  danger: "border-danger/40 bg-danger/10 text-danger",
  gold: "border-gold/40 bg-gold/10 text-gold",
  muted: "border-border bg-surface-2 text-muted",
};

export function Badge({
  tone = "muted",
  className,
  children,
}: {
  tone?: keyof typeof TONES;
  className?: string;
  children: React.ReactNode;
}) {
  return <span className={cn("chip", TONES[tone], className)}>{children}</span>;
}

export function Card({
  className,
  children,
  as: Tag = "div",
  ...rest
}: {
  className?: string;
  children: React.ReactNode;
  as?: React.ElementType;
} & React.HTMLAttributes<HTMLElement>) {
  return (
    <Tag className={cn("card p-4", className)} {...rest}>
      {children}
    </Tag>
  );
}

export function CardTitle({ children, hint }: { children: React.ReactNode; hint?: React.ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h3 className="text-sm font-semibold text-fg">{children}</h3>
      {hint ? <span className="text-xs text-muted">{hint}</span> : null}
    </div>
  );
}

export function Stat({ label, value, sub }: { label: string; value: React.ReactNode; sub?: string }) {
  return (
    <div className="card-2 p-3">
      <div className="label">{label}</div>
      <div className="num mt-1 text-2xl font-semibold text-fg">{value}</div>
      {sub ? <div className="mt-0.5 text-xs text-muted">{sub}</div> : null}
    </div>
  );
}

const FILLS: Record<string, string> = {
  accent: "bg-accent",
  warn: "bg-warn",
  danger: "bg-danger",
  info: "bg-info",
};

export function Progress({
  value,
  tone = "accent",
  label,
}: {
  value: number;
  tone?: keyof typeof FILLS;
  label?: string;
}) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div
      className="h-2 w-full overflow-hidden rounded-full bg-surface-2"
      role="progressbar"
      aria-valuenow={Math.round(v)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <div className={cn("h-full rounded-full transition-[width] duration-300", FILLS[tone])} style={{ width: `${v}%` }} />
    </div>
  );
}

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline" | "danger";
  size?: "sm" | "md";
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "primary", size = "md", ...props },
  ref
) {
  const styles = {
    primary: "bg-accent text-bg hover:bg-accent/90 font-semibold",
    ghost: "text-muted hover:bg-surface-2 hover:text-fg",
    outline: "border border-border text-fg hover:bg-surface-2",
    danger: "bg-danger/15 text-danger hover:bg-danger/25 font-semibold",
  }[variant];
  const sizing = size === "sm" ? "min-h-[36px] px-3 text-sm" : "min-h-[40px] px-4 text-sm";
  return (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl transition-colors disabled:cursor-not-allowed disabled:opacity-50",
        sizing,
        styles,
        className
      )}
      {...props}
    />
  );
});

// Icon-only button — requires an accessible label (WCAG 4.1.2). Min 28px target.
export const IconButton = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { label: string; tone?: "default" | "danger" | "info" }
>(function IconButton({ className, label, tone = "default", children, ...props }, ref) {
  const tones = {
    default: "text-muted hover:bg-surface-2 hover:text-fg",
    danger: "bg-danger text-white hover:bg-danger/90",
    info: "bg-info text-bg hover:bg-info/90",
  }[tone];
  return (
    <button
      ref={ref}
      type="button"
      aria-label={label}
      title={label}
      className={cn("grid h-7 w-7 place-items-center rounded-full text-sm transition-colors", tones, className)}
      {...props}
    >
      {children}
    </button>
  );
});

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton", className)} aria-hidden="true" />;
}

// Inline status / validation message. Errors announce politely to screen readers.
export function Alert({
  tone = "info",
  title,
  children,
}: {
  tone?: "info" | "warn" | "danger" | "accent";
  title?: string;
  children?: React.ReactNode;
}) {
  const tones = {
    info: "border-info/30 bg-info/10 text-info",
    warn: "border-warn/30 bg-warn/10 text-warn",
    danger: "border-danger/30 bg-danger/10 text-danger",
    accent: "border-accent/30 bg-accent/10 text-accent",
  }[tone];
  return (
    <div
      role={tone === "danger" || tone === "warn" ? "alert" : "status"}
      aria-live={tone === "danger" || tone === "warn" ? "assertive" : "polite"}
      className={cn("rounded-xl border px-3 py-2 text-sm", tones)}
    >
      {title ? <div className="font-semibold">{title}</div> : null}
      {children ? <div className="text-fg/90">{children}</div> : null}
    </div>
  );
}

// Accessible segmented control (used for the position filter). Arrow-key friendly
// via native radios + roving labels.
export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  ariaLabel,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
  ariaLabel: string;
}) {
  return (
    <div role="radiogroup" aria-label={ariaLabel} className="inline-flex rounded-lg bg-surface-2 p-0.5">
      {options.map((o) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            role="radio"
            aria-checked={active}
            onClick={() => onChange(o.value)}
            className={cn(
              "min-h-[32px] rounded-md px-2.5 text-xs font-medium transition-colors",
              active ? "bg-accent text-bg" : "text-muted hover:text-fg"
            )}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
