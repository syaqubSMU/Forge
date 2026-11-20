import type { Metadata } from "next";
import { Button } from "antd";
import HeroCollage, { type Grade } from "@/components/home/HeroCollage";
import PageHero from "@/components/common/PageHero";
import CTAButton from "@/components/common/CTAButton";

export const metadata: Metadata = { title: "Design options", robots: { index: false, follow: false } };

const grades: { key: Grade; name: string; note: string }[] = [
  { key: "brand", name: "A · Brand blue", note: "Current. Cool blue shadows with a hint of coral." },
  { key: "orange", name: "B · Orange", note: "Whole collage graded warm orange." },
  { key: "light-orange", name: "C · Light orange", note: "Soft peach wash, lifted and airy." },
  { key: "sunset", name: "D · Sunset", note: "Tangerine to coral highlights, blue in the shadows." },
];

export default function DesignOptions() {
  return (
    <>
      <PageHero eyebrow="Internal preview" title="Colour grade & button options" text="Not linked from the site. Tell me the letter you prefer." />
      <section className="section">
        <div className="container" style={{ display: "grid", gap: 36 }}>
          {grades.map((g) => (
            <div key={g.key}>
              <h2 style={{ fontSize: 22 }}>{g.name}</h2>
              <p style={{ color: "var(--muted)", margin: "4px 0 14px" }}>{g.note}</p>
              <div className="options-band" style={{ maxWidth: 640 }}><HeroCollage grade={g.key} /></div>
            </div>
          ))}
          <div>
            <h2 style={{ fontSize: 22, marginBottom: 14 }}>Buttons: before and after</h2>
            <div className="options-band" style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
              <Button size="large" style={{ background: "#CF4126", borderColor: "#CF4126", color: "#fff" }}>Before (flat)</Button>
              <CTAButton href="/book-consultation">After (glossy)</CTAButton>
              <CTAButton href="/solutions" tone="ghost-light">Glass secondary</CTAButton>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
