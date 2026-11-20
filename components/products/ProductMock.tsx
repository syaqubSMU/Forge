/** Dashboard-style placeholder illustration (not a real screenshot). */
export default function ProductMock({ label }: { label: string }) {
  return (
    <div className="pmock" role="img" aria-label={`Illustrative preview of ${label}`}>
      <svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <rect width="400" height="250" fill="#F6F5F2" />
        <g stroke="#DCE3EA" strokeWidth="1"><path d="M0 62H400M0 124H400M0 186H400M100 0V250M200 0V250M300 0V250" /></g>
        <rect x="24" y="22" width="352" height="206" rx="10" fill="#fff" stroke="#CBD5E1" />
        <rect x="24" y="22" width="352" height="30" rx="10" fill="#174A82" /><rect x="24" y="40" width="352" height="12" fill="#174A82" />
        <circle cx="40" cy="37" r="3.5" fill="#F25C3C" /><circle cx="52" cy="37" r="3.5" fill="#F4A261" /><circle cx="64" cy="37" r="3.5" fill="#fff" opacity=".7" />
        <rect x="260" y="33" width="100" height="8" rx="4" fill="#fff" opacity=".25" />
        <g fill="#E8EDF3"><rect x="40" y="66" width="140" height="8" rx="4" /><rect x="40" y="84" width="96" height="8" rx="4" /></g>
        <g fill="#174A82">{[[44, 30], [76, 44], [108, 38], [140, 60], [172, 52]].map(([x, h]) => <rect key={x} x={x} y={192 - h} width="20" height={h} rx="3" />)}</g>
        <rect x="204" y="132" width="20" height="60" rx="3" fill="#F25C3C" />
        <path d="M44 150 L82 138 L114 142 L146 120 L178 124 L214 100 L260 84" fill="none" stroke="#F4A261" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        <g fill="#E8EDF3">{[0, 1, 2, 3].map((i) => <rect key={i} x="250" y={112 + i * 20} width="110" height="10" rx="3" />)}</g>
        <g fill="#1E8E5A">{[0, 1, 2, 3].map((i) => <circle key={i} cx="262" cy={117 + i * 20} r="3" />)}</g>
        <line x1="40" y1="196" x2="360" y2="196" stroke="#CBD5E1" />
      </svg>
      <span className="tag">Illustrative preview</span>
    </div>
  );
}
