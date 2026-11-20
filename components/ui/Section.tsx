import type { ReactNode } from "react";
type Props = { id?: string; tone?: "white" | "soft" | "warm" | "blue"; children: ReactNode; className?: string };
export default function Section({ id, tone = "white", children, className = "" }: Props) {
  return <section id={id} className={`section section--${tone} ${className}`}><div className="container">{children}</div></section>;
}
export function SectionHeading({ eyebrow, title, text, align = "left" }: { eyebrow?: string; title: string; text?: string; align?: "left" | "center" }) {
  return (
    <div className={`sh sh--${align}`}>
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      <h2>{title}</h2>
      {text && <p className="lead">{text}</p>}
    </div>
  );
}
export function PageHero({ eyebrow, title, text, children }: { eyebrow?: string; title: string; text?: string; children?: ReactNode }) {
  return (
    <section className="page-hero"><div className="container">
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      <h1>{title}</h1>
      {text && <p className="lead">{text}</p>}
      {children && <div className="btn-row">{children}</div>}
    </div></section>
  );
}
