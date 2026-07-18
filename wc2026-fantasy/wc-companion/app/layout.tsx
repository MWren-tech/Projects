import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "WC2026 Fantasy Companion",
  description: "AI fantasy football companion for the FIFA World Cup 2026",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <a href="#main" className="skip-link rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-bg">
          Skip to content
        </a>
        <div className="flex min-h-screen">
          <Sidebar />
          <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
