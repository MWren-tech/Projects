"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, MessageSquare, Users, ArrowLeftRight, Zap, BarChart3, Trophy,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "AI Assistant", icon: MessageSquare },
  { href: "/squad", label: "Squad Builder", icon: Users },
  { href: "/players", label: "Players", icon: BarChart3 },
  { href: "/transfers", label: "Transfer Planner", icon: ArrowLeftRight },
  { href: "/boosts", label: "Boost Strategy", icon: Zap },
  { href: "/compare", label: "Compare", icon: Trophy },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-border bg-surface/60 p-4 backdrop-blur md:flex">
      <div className="mb-6 flex items-center gap-2 px-2">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-bg font-black">26</div>
        <div>
          <div className="text-sm font-semibold leading-tight text-fg">WC2026</div>
          <div className="text-[11px] text-muted">Fantasy Companion</div>
        </div>
      </div>
      <nav className="flex flex-col gap-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? path === "/" : path.startsWith(href);
          return (
            <Link key={href} href={href} className={cn("nav-item", active && "nav-item-active")}>
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto card-2 p-3 text-[11px] leading-relaxed text-muted">
        Numbers come from the validated WC engine. Re-run{" "}
        <code className="text-accent">npm run snapshot</code> after each matchday.
      </div>
    </aside>
  );
}
