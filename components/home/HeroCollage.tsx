import { site } from "@/lib/content";
import { withBase } from "@/lib/path";

const SKIN1 = "#E3A77F", SKIN2 = "#8A5A3B", SKIN3 = "#C98E67";

function Scientists() {
  return (
    <svg viewBox="0 0 240 190" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Illustration of two scientists working in a laboratory">
      <rect width="240" height="190" fill="#E6F0FA" />
      <g stroke="#174A82" strokeOpacity=".3" strokeWidth="2"><line x1="24" y1="34" x2="48" y2="50" /><line x1="48" y1="50" x2="72" y2="34" /><line x1="48" y1="50" x2="48" y2="76" /></g>
      <circle cx="24" cy="34" r="7" fill="#174A82" /><circle cx="48" cy="50" r="9" fill="#F25C3C" /><circle cx="72" cy="34" r="6" fill="#F4A261" /><circle cx="48" cy="76" r="6" fill="#174A82" opacity=".6" />
      <rect x="150" y="34" width="80" height="5" rx="2" fill="#174A82" opacity=".3" />
      <rect x="160" y="18" width="10" height="16" rx="2" fill="#F4A261" /><circle cx="194" cy="25" r="9" fill="#CF4126" opacity=".85" /><rect x="210" y="20" width="9" height="14" rx="2" fill="#174A82" opacity=".7" />
      <rect y="140" width="240" height="50" fill="#BFD3E8" /><rect y="136" width="240" height="8" fill="#174A82" />
      {/* microscope */}
      <rect x="128" y="130" width="28" height="6" rx="2" fill="#174A82" />
      <rect x="146" y="98" width="6" height="34" rx="2" fill="#174A82" />
      <path d="M149 100 Q132 96 130 116" stroke="#174A82" strokeWidth="6" fill="none" strokeLinecap="round" />
      <rect x="123" y="86" width="9" height="26" rx="3" transform="rotate(-12 127 99)" fill="#F4A261" />
      {/* person 1 */}
      <rect x="44" y="84" width="42" height="56" rx="13" fill="#fff" stroke="#C3D2E3" strokeWidth="1.5" />
      <path d="M57 84 L65 102 L73 84Z" fill="#174A82" />
      <circle cx="65" cy="66" r="15" fill={SKIN1} />
      <path d="M50 65 a15 15 0 0 1 30 0 q-15 -9 -30 0z" fill="#3A2A22" />
      <rect x="55" y="63" width="20" height="7" rx="3.5" fill="#BFE6F2" stroke="#174A82" strokeWidth="1.5" />
      <path d="M82 98 Q100 100 106 114" stroke="#C3D2E3" strokeWidth="12" strokeLinecap="round" fill="none" />
      <path d="M82 98 Q100 100 106 114" stroke="#fff" strokeWidth="10" strokeLinecap="round" fill="none" />
      <circle cx="107" cy="116" r="5" fill={SKIN1} />
      <rect x="104" y="96" width="7" height="10" fill="#fff" stroke="#9FB6CE" />
      <path d="M104 106 L96 128 Q95 133 100 133 H118 Q123 133 122 128 L114 106Z" fill="#fff" fillOpacity=".85" stroke="#9FB6CE" strokeWidth="1.5" />
      <path d="M99 122 H119 L121 128 Q122 132 118 132 H100 Q96 132 97 128Z" fill="#F25C3C" />
      {/* person 2 */}
      <rect x="172" y="92" width="42" height="48" rx="13" fill="#fff" stroke="#C3D2E3" strokeWidth="1.5" />
      <path d="M185 92 L193 108 L201 92Z" fill="#16A6A1" />
      <circle cx="190" cy="74" r="14" fill={SKIN2} />
      <path d="M176 72 a14 14 0 0 1 28 0 q-14 -8 -28 0z" fill="#1E1A18" />
      <path d="M174 106 Q160 112 152 112" stroke="#C3D2E3" strokeWidth="12" strokeLinecap="round" fill="none" />
      <path d="M174 106 Q160 112 152 112" stroke="#fff" strokeWidth="10" strokeLinecap="round" fill="none" />
      <circle cx="151" cy="112" r="5" fill={SKIN2} />
    </svg>
  );
}

function Economists() {
  return (
    <svg viewBox="0 0 240 190" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Illustration of economists presenting a growth chart and working at a desk">
      <rect width="240" height="190" fill="#FFF0E3" />
      <rect x="80" y="14" width="146" height="100" rx="8" fill="#fff" stroke="#F0D2B6" strokeWidth="2" />
      <line x1="94" y1="98" x2="212" y2="98" stroke="#E5E0D8" strokeWidth="2" />
      {[[98, 18], [120, 28], [142, 38], [164, 52], [186, 64]].map(([x, h], i) => (
        <rect key={x} x={x} y={98 - h} width="16" height={h} rx="3" fill={i === 4 ? "#F25C3C" : "#174A82"} opacity={i === 4 ? 1 : 0.85} />
      ))}
      <polyline points="106,70 128,60 150,50 172,36 196,22" fill="none" stroke="#F4A261" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M188 20 L199 20 L199 31" fill="none" stroke="#F4A261" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
      {/* presenter */}
      <rect x="18" y="90" width="42" height="62" rx="13" fill="#174A82" />
      <path d="M31 90 L39 110 L47 90Z" fill="#fff" /><path d="M37 100 h4 l2 14 l-4 4 l-4 -4z" fill="#F25C3C" />
      <circle cx="39" cy="68" r="14" fill={SKIN3} />
      <path d="M25 66 a14 14 0 0 1 28 0 q-14 -9 -28 0z" fill="#2B211C" />
      <path d="M58 102 Q72 100 84 86" stroke="#174A82" strokeWidth="11" strokeLinecap="round" fill="none" />
      <circle cx="85" cy="85" r="5" fill={SKIN3} />
      {/* colleague */}
      <rect x="168" y="132" width="38" height="24" rx="10" fill="#315B7D" />
      <circle cx="187" cy="124" r="12" fill={SKIN1} />
      <path d="M175 122 a12 12 0 0 1 24 0 q-12 -8 -24 0z" fill="#5A3A22" />
      {/* desk, laptop, cup */}
      <rect y="150" width="240" height="40" fill="#E4C9AB" /><rect y="146" width="240" height="8" fill="#174A82" />
      <rect x="160" y="128" width="54" height="20" rx="4" fill="#CBD5E1" /><circle cx="187" cy="138" r="3" fill="#94A3B8" />
      <rect x="112" y="136" width="12" height="12" rx="2" fill="#fff" stroke="#C3D2E3" /><rect x="112" y="136" width="12" height="4" fill="#CF4126" />
    </svg>
  );
}

const checks = [
  ["Award terms recorded", "Done"],
  ["Reports & deadlines tracked", "On track"],
  ["Budgets monitored", "On track"],
  ["Documents filed", "Done"],
];

function Tile({ photo, alt, children, label, className }: { photo?: string; alt: string; children: React.ReactNode; label: string; className?: string }) {
  return (
    <div className={`tile graded ${className ?? ""}`}>
      {photo ? /* eslint-disable-next-line @next/next/no-img-element */ <img src={withBase(photo)} alt={alt} /> : children}
      <span className="cap">{label}</span>
    </div>
  );
}

export type Grade = "brand" | "orange" | "light-orange" | "sunset";
export default function HeroCollage({ grade = site.heroGrade as Grade }: { grade?: Grade }) {
  const { scientists, economists } = site.heroPhotos;
  return (
    <div className="collage" data-grade={grade}>
      <div className="collage-left">
        <Tile photo={scientists} alt="Scientists working in a laboratory" label="Scientists"><Scientists /></Tile>
        <Tile photo={economists} alt="Economists analysing data" label="Economists"><Economists /></Tile>
      </div>
      <div className="tile pc-tile" role="img" aria-label="Computer screen reading: your grants are being managed, with a checklist and an upward-trending graph">
        <div className="pc-screen">
          <div className="pc-top"><b>Your grants are being managed</b><span className="pill">Sample</span></div>
          <p className="pc-agent"><i aria-hidden="true" className="pulse" />Your grant agent is managing the tracking while you do the real work.</p>
          <ul className="pc-list">
            {checks.map(([t, s]) => (
              <li key={t}>
                <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="9" fill="#1E8E5A" /><path d="M5 9.3 7.9 12 13 6.3" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                <span>{t}</span><em>{s}</em>
              </li>
            ))}
          </ul>
          <div className="pc-graph">
            <div className="pc-graph-label">Grant visibility <span aria-hidden="true">↑</span></div>
            <div className="pc-plot">
            <svg viewBox="0 0 200 84" preserveAspectRatio="none" aria-hidden="true">
              <defs><linearGradient id="gArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#174A82" stopOpacity=".28" /><stop offset="1" stopColor="#174A82" stopOpacity="0" /></linearGradient></defs>
              <g stroke="#E2E0DA" strokeWidth="1"><line x1="0" y1="20" x2="200" y2="20" /><line x1="0" y1="45" x2="200" y2="45" /><line x1="0" y1="70" x2="200" y2="70" /></g>
              <path d="M0 74 L30 66 L58 69 L88 50 L118 54 L150 30 L180 20 L200 8 V84 H0Z" fill="url(#gArea)" />
              <polyline points="0,74 30,66 58,69 88,50 118,54 150,30 180,20 200,8" fill="none" stroke="#174A82" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
            </svg>
            <i className="pc-dot" aria-hidden="true" />
            </div>
          </div>
        </div>
        <div className="pc-stand" aria-hidden="true" />
        <span className="cap">Illustrative</span>
      </div>
    </div>
  );
}
