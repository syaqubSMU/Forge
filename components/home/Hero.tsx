import CTAButton from "../common/CTAButton";
import Infinity from "../common/Infinity";
import HeroCollage from "./HeroCollage";

export default function Hero() {
  return (
    <section className="hero">
      <Infinity className="watermark" tone="light" />
      <div className="container hero-grid">
        <div>
          <h1>Better Grant Management Starts with Better Systems.</h1>
          <p className="lead">
            Winning a grant is only the beginning. Forge helps nonprofits build the systems, financial controls, compliance workflows, and technology needed to manage grant-funded programs effectively.
          </p>
          <div className="cta-row">
            <CTAButton href="/book-consultation" event="consultation_cta_clicked">Book a Consultation</CTAButton>
            <CTAButton href="/solutions" tone="ghost-light">Explore Our Solutions</CTAButton>
          </div>
        </div>
        <HeroCollage />
      </div>
    </section>
  );
}
