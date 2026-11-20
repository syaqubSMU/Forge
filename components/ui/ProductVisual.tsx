import type { Product } from "@/lib/content";
const B = "#244B70", C = "#E98262", S = "#EFF4F8", L = "#D9E2EA";
const rows = (n: number, y0: number, x = 36, w = 328, gap = 22) => Array.from({ length: n }, (_, i) => <rect key={i} x={x} y={y0 + i * gap} width={i % 3 === 2 ? w * 0.7 : w} height="9" rx="4.5" fill={L} />);

export default function ProductVisual({ kind, label }: { kind: Product["visual"]; label: string }) {
  let inner;
  switch (kind) {
    case "tracker": inner = (<><rect x="24" y="24" width="352" height="30" rx="8" fill={B} />{[0, 1, 2, 3, 4].map((i) => (<g key={i}><rect x="36" y={70 + i * 32} width="90" height="10" rx="5" fill={L} /><rect x="140" y={70 + i * 32} width="110" height="10" rx="5" fill={L} /><rect x="268" y={67 + i * 32} width="84" height="16" rx="8" fill={i === 1 ? C : S} stroke={i === 1 ? C : "#C8D8E6"} /></g>))}</>); break;
    case "budget": inner = (<>{[0, 1, 2, 3].map((i) => (<g key={i}><rect x="36" y={42 + i * 44} width="328" height="16" rx="8" fill={L} /><rect x="36" y={42 + i * 44} width={150 + i * 28} height="16" rx="8" fill={B} /><rect x={36 + 150 + i * 28} y={42 + i * 44} width={56 - i * 6} height="16" fill={C} /></g>))}<rect x="36" y="210" width="120" height="10" rx="5" fill={L} /></>); break;
    case "travel": inner = (<><rect x="110" y="24" width="180" height="200" rx="14" fill="#fff" stroke={L} strokeWidth="2" /><rect x="124" y="38" width="152" height="40" rx="8" fill={S} /><rect x="136" y="52" width="70" height="12" rx="6" fill={B} />{[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (<rect key={i} x={124 + (i % 3) * 52} y={92 + Math.floor(i / 3) * 42} width="44" height="34" rx="8" fill={i === 8 ? C : S} />))}</>); break;
    case "calendar": inner = (<><rect x="30" y="24" width="340" height="30" rx="8" fill={B} />{Array.from({ length: 28 }, (_, i) => (<rect key={i} x={36 + (i % 7) * 47} y={66 + Math.floor(i / 7) * 40} width="40" height="32" rx="6" fill={[4, 11, 19].includes(i) ? C : i % 5 === 0 ? "#C8D8E6" : S} />))}</>); break;
    case "templates": inner = (<>{[0, 1, 2, 3].map((i) => (<g key={i}><rect x="40" y={40 + i * 46} width="22" height="22" rx="5" fill={i < 2 ? B : "#fff"} stroke={B} strokeWidth="2" /><rect x="76" y={46 + i * 46} width={220 - i * 20} height="10" rx="5" fill={L} /></g>))}</>); break;
    case "sop": inner = (<><rect x="90" y="20" width="220" height="210" rx="10" fill="#fff" stroke={L} strokeWidth="2" /><rect x="110" y="42" width="120" height="14" rx="7" fill={B} />{rows(7, 74, 110, 180, 20)}<rect x="110" y="214" width="46" height="8" rx="4" fill={C} /></>); break;
    default: inner = (<>{[0, 1, 2, 3, 4, 5].map((i) => (<g key={i}><rect x={36 + (i % 3) * 112} y={36 + Math.floor(i / 3) * 96} width="100" height="84" rx="10" fill="#fff" stroke={L} strokeWidth="2" /><rect x={48 + (i % 3) * 112} y={50 + Math.floor(i / 3) * 96} width="46" height="9" rx="4.5" fill={i === 4 ? C : B} />{rows(2, 70 + Math.floor(i / 3) * 96, 48 + (i % 3) * 112, 76, 14)}</g>))}</>);
  }
  return (
    <div className="pv" role="img" aria-label={`Illustrative preview of ${label}`}>
      <svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="400" height="250" fill="#F3F4F2" />{inner}</svg>
    </div>
  );
}
