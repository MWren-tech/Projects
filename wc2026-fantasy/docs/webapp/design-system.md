# Design system & accessibility

Reference implementation: the **Squad Builder**. New UI should match its quality bar.

## Tokens
- Defined in `app/globals.css` (`:root`) + `tailwind.config.ts`.
- Colours: `bg / surface / surface-2 / border / muted / fg / accent` + semantic `info/warn/danger/gold` + position colours `gk/def/mid/fwd`. `muted` is tuned to ≥ ~5:1 contrast.
- Radii (`--radius-*`), elevation (`--elev-*`), focus ring (`--ring`).
- Spacing/typography on a 4-pt rhythm (Tailwind scale).

## Primitives (`components/ui/primitives.tsx`)
`Button` (variants/sizes, ≥40px target), `IconButton` (label required), `Badge`, `Progress` (ARIA), `Alert` (role + aria-live), `Skeleton`, `SegmentedControl` (radiogroup), `Card`, `CardTitle`, `Stat`. Keep these **backward-compatible**.

## Accessibility (WCAG 2.2 AA — required)
- Visible **`:focus-visible`** ring everywhere; **skip-to-content** link in the layout.
- All actionable controls **keyboard-operable** and labelled (icon buttons need `aria-label`). Hover-only affordances must also reveal on **focus-within** (don't use `hidden`, which drops them from the tab order).
- **Focus trap + return focus** in modals (`role="dialog"`, `aria-modal`).
- Validation messages use `Alert` (`role`/`aria-live`).
- Respect `prefers-reduced-motion`; avoid unnecessary animation.
- Minimum target size ≥ 24px (aim 28–40).

## UX principles applied
- **Visibility of system status** — sticky status bar (budget, completion, formation, validity).
- **Progressive disclosure** — detailed transfer choices in a modal, not on the pitch.
- **Gestalt / proximity** — consistent cards, grouped position pips.
- **Hick / Fitts** — filtered choices (segmented control + search), large primary actions.
- **States** — every surface covers hover / focus / loading / empty / error.

## Status
- ✅ Squad Builder fully at AA.
- 🔜 Roll the same to Dashboard, Players, Transfers, Boosts, Chat, Compare (ROADMAP P2).
