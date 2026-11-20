import data from "./logoData.json";

type Props = { variant?: "horizontal" | "stacked" | "icon" | "wordmark"; tone?: "light" | "dark"; height?: number; className?: string };

/**
 * FORGE logo system (Sora Bold letterforms as outlines, no webfont dependency). Files also live in /public/brand.
 * "horizontal" is the integrated wordmark: the logo mark IS the F (blue stem and top arm, coral middle arm) followed by ORGE.
 * `height` is the cap height of the lettering in px (stacked: total height).
 */
export default function Logo({ variant = "horizontal", tone = "light", height = 28, className }: Props) {
  const word = tone === "light" ? "#244B70" : "#FFFFFF";
  const desc = tone === "light" ? "#344452" : "#C9D6E3";
  const coral = "#E98262";
  const svgProps = { className, height, role: "img" as const, "aria-label": "FORGE" };
  const F = (
    <>
      {(["stem", "top"] as const).map((k) => { const r = data.rects[k]; return <rect key={k} x={r[0]} y={r[1]} width={r[2]} height={r[3]} fill={word} />; })}
      <rect x={data.rects.mid[0]} y={data.rects.mid[1]} width={data.rects.mid[2]} height={data.rects.mid[3]} fill={coral} />
    </>
  );
  if (variant === "icon") {
    const html = data.iconShapes.replaceAll('"STEM"', `"${word}"`).replaceAll('"ARM"', `"${coral}"`);
    return <svg {...svgProps} viewBox="0 0 48 48" dangerouslySetInnerHTML={{ __html: html }} />;
  }
  if (variant === "wordmark")
    return <svg {...svgProps} viewBox={`0 ${-data.wordOnlyViewBox[1]} ${data.wordOnlyViewBox[0]} ${data.wordOnlyViewBox[1]}`}><path d={data.wordOnlyPath} fill={word} /></svg>;
  if (variant === "stacked")
    return (
      <svg {...svgProps} aria-label="FORGE — Connected research operations" viewBox={`0 0 ${data.stackW} ${data.stackH}`}>
        {F}<path d={data.orge} fill={word} /><g transform={`translate(${data.descX} ${data.descY})`}><path d={data.descPath} fill={desc} /></g>
      </svg>
    );
  return <svg {...svgProps} viewBox={`0 0 ${data.W} ${data.H}`}>{F}<path d={data.orge} fill={word} /></svg>;
}
