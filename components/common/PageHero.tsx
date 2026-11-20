import Infinity from "./Infinity";
import type { ReactNode } from "react";
export default function PageHero({ eyebrow, title, text, children }: { eyebrow?: string; title: string; text?: string; children?: ReactNode }) {
  return (
    <section className="page-hero">
      <Infinity className="watermark" tone="dark" />
      <div className="container">
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {text && <p className="lead">{text}</p>}
        {children && <div className="cta-row" style={{ marginTop: 24 }}>{children}</div>}
      </div>
    </section>
  );
}
