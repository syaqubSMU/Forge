import data from "./logoData.json";

type Props = { variant?: "horizontal" | "stacked" | "icon" | "wordmark"; tone?: "light" | "dark"; height?: number; className?: string };

/** FORGE logo system rendered from outlined Sora letterforms (no webfont dependency). Files also live in /public/brand. */
export default function Logo({ variant = "horizontal", tone = "light", height = 32, className }: Props) {
  const word = tone === "light" ? "#244B70" : "#FFFFFF";
  const desc = tone === "light" ? "#344452" : "#C9D6E3";
  const coral = "#E98262";
  const icon = (stem: string) => data.iconShapes.replaceAll('"STEM"', `"${stem}"`).replaceAll('"ARM"', `"${coral}"`);
  const svgProps = { className, height, role: "img" as const, "aria-label": "FORGE" };
  if (variant === "icon")
    return <svg {...svgProps} viewBox="0 0 48 48" dangerouslySetInnerHTML={{ __html: icon(word) }} />;
  if (variant === "wordmark")
    return <svg {...svgProps} viewBox={`0 ${-data.wordOnlyViewBox[1]} ${data.wordOnlyViewBox[0]} ${data.wordOnlyViewBox[1]}`}><path d={data.wordOnlyPath} fill={word} /></svg>;
  if (variant === "stacked")
    return (
      <svg {...svgProps} aria-label="FORGE — Connected research operations" viewBox={`0 0 ${data.stackW} ${data.stackH}`}>
        <g transform={`translate(${data.lockX} 0)`}><g transform={`scale(${data.hScale})`} dangerouslySetInnerHTML={{ __html: icon(word) }} /><path d={data.wordPath} fill={word} /></g>
        <g transform={`translate(${data.descX} ${data.descY})`}><path d={data.descPath} fill={desc} /></g>
      </svg>
    );
  return (
    <svg {...svgProps} viewBox={`0 0 ${data.hViewBox[0]} ${data.hViewBox[1]}`}>
      <g transform={`scale(${data.hScale})`} dangerouslySetInnerHTML={{ __html: icon(word) }} /><path d={data.wordPath} fill={word} />
    </svg>
  );
}
