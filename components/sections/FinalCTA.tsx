import Section from "../ui/Section";
import Button from "../ui/Button";
export default function FinalCTA({ title = "See how FORGE could simplify your research operations.", text = "Book a discovery call to talk through your portfolio, your team and your current systems. No obligation and no sales pressure.", cta = "Book a Discovery Call", href = "/book-discovery-call" }: { title?: string; text?: string; cta?: string; href?: string }) {
  return (
    <Section tone="blue">
      <div style={{ textAlign: "center", maxWidth: 760, margin: "0 auto" }}>
        <h2>{title}</h2><p className="lead" style={{ margin: "18px auto 30px" }}>{text}</p>
        <Button href={href} variant="accent" size="lg" event="consultation_cta_clicked">{cta}</Button>
      </div>
    </Section>
  );
}
