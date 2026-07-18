// National-team kit colours (primary shirt fill + readable text/accent) and short
// codes, plus the fixture-difficulty colour scale used on the pitch.

export interface Kit {
  bg: string;
  text: string;
}

export const KITS: Record<string, Kit> = {
  Algeria: { bg: "#0a7a3b", text: "#ffffff" },
  Argentina: { bg: "#6cace4", text: "#0b2a52" },
  Australia: { bg: "#f5c518", text: "#00563f" },
  Austria: { bg: "#ed2939", text: "#ffffff" },
  Belgium: { bg: "#c8102e", text: "#fdda24" },
  "Bosnia and Herzegovina": { bg: "#1e3a8a", text: "#f5c518" },
  Brazil: { bg: "#ffdf00", text: "#009c3b" },
  Canada: { bg: "#d80621", text: "#ffffff" },
  Colombia: { bg: "#fcd116", text: "#003893" },
  Croatia: { bg: "#d10a11", text: "#ffffff" },
  Curacao: { bg: "#0038a8", text: "#ffffff" },
  Czechia: { bg: "#d7141a", text: "#ffffff" },
  "DR Congo": { bg: "#007fff", text: "#f7d618" },
  Ecuador: { bg: "#ffd100", text: "#0072c6" },
  Egypt: { bg: "#ce1126", text: "#ffffff" },
  England: { bg: "#f4f4f4", text: "#1d3a8a" },
  France: { bg: "#1a47b8", text: "#ffffff" },
  Germany: { bg: "#efefef", text: "#111111" },
  Ghana: { bg: "#ffffff", text: "#006b3f" },
  Haiti: { bg: "#00209f", text: "#d21034" },
  "Ivory Coast": { bg: "#ff7f00", text: "#ffffff" },
  Japan: { bg: "#0c1c8c", text: "#ffffff" },
  Jordan: { bg: "#f4f4f4", text: "#ce1126" },
  Mexico: { bg: "#006847", text: "#ffffff" },
  Morocco: { bg: "#c1272d", text: "#006233" },
  Netherlands: { bg: "#ff6900", text: "#ffffff" },
  "New Zealand": { bg: "#efefef", text: "#111111" },
  Norway: { bg: "#ba0c2f", text: "#ffffff" },
  Panama: { bg: "#d21034", text: "#ffffff" },
  Paraguay: { bg: "#d52b1e", text: "#ffffff" },
  Portugal: { bg: "#a4123f", text: "#0c6b37" },
  "Saudi Arabia": { bg: "#006c35", text: "#ffffff" },
  Scotland: { bg: "#0e2a52", text: "#ffffff" },
  Senegal: { bg: "#ffffff", text: "#00853f" },
  "South Africa": { bg: "#007a4d", text: "#ffb612" },
  "South Korea": { bg: "#c70025", text: "#ffffff" },
  Spain: { bg: "#c60b1e", text: "#f1bf00" },
  Sweden: { bg: "#fecc00", text: "#006aa7" },
  Switzerland: { bg: "#d52b1e", text: "#ffffff" },
  Tunisia: { bg: "#e70013", text: "#ffffff" },
  Turkey: { bg: "#e30a17", text: "#ffffff" },
  USA: { bg: "#002868", text: "#ffffff" },
  Uruguay: { bg: "#5da9e9", text: "#0b2a52" },
  Uzbekistan: { bg: "#0099b5", text: "#ffffff" },
};

const DEFAULT_KIT: Kit = { bg: "#2a2f3a", text: "#e7ecf3" };

export function kitFor(nation: string): Kit {
  return KITS[nation] ?? DEFAULT_KIT;
}

const ABBR: Record<string, string> = {
  "Bosnia and Herzegovina": "BIH", "DR Congo": "COD", "Ivory Coast": "CIV",
  "New Zealand": "NZL", "Saudi Arabia": "KSA", "South Africa": "RSA",
  "South Korea": "KOR", "Czechia": "CZE", Curacao: "CUW", Netherlands: "NED",
  Switzerland: "SUI", Portugal: "POR", Argentina: "ARG", Australia: "AUS",
  Germany: "GER", England: "ENG", France: "FRA", Belgium: "BEL", Croatia: "CRO",
  Uruguay: "URU", Colombia: "COL", Morocco: "MAR", Senegal: "SEN", Japan: "JPN",
  Mexico: "MEX", USA: "USA", Canada: "CAN", Spain: "ESP", Brazil: "BRA",
  Norway: "NOR", Sweden: "SWE", Egypt: "EGY", Ghana: "GHA", Tunisia: "TUN",
  Algeria: "ALG", Ecuador: "ECU", Paraguay: "PAR", Panama: "PAN", Haiti: "HAI",
  Jordan: "JOR", Uzbekistan: "UZB", Austria: "AUT", Scotland: "SCO", Turkey: "TUR",
};

export function abbr(nation: string | null | undefined): string {
  if (!nation) return "TBD";
  return ABBR[nation] ?? nation.slice(0, 3).toUpperCase();
}

// Fixture-difficulty colour scale (matches the EaseBadge wording):
//   green easy · blue favourable · grey neutral · orange tough · red very tough
export function easeColor(value: number | null | undefined): { bg: string; text: string; label: string } {
  if (value == null) return { bg: "rgba(139,148,163,.18)", text: "#8b94a3", label: "—" };
  if (value >= 1.25) return { bg: "rgba(62,230,160,.18)", text: "#3ee6a0", label: "Easy" };
  if (value >= 1.05) return { bg: "rgba(90,169,255,.18)", text: "#5aa9ff", label: "Favourable" };
  if (value >= 0.95) return { bg: "rgba(139,148,163,.18)", text: "#a7b0bf", label: "Neutral" };
  if (value >= 0.85) return { bg: "rgba(255,180,84,.18)", text: "#ffb454", label: "Tough" };
  return { bg: "rgba(255,93,108,.18)", text: "#ff5d6c", label: "Very tough" };
}
