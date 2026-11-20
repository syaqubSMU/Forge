import CTAButton from "./CTAButton";
export default function FinalCTA({
  title = "Ready to Bring More Structure to Your Grant Operations?",
  text = "Let's identify where your current processes can improve and build a more manageable grant operations environment.",
  cta = "Book a Consultation",
}: { title?: string; text?: string; cta?: string }) {
  return (
    <section className="final-cta">
      <div className="container">
        <h2>{title}</h2>
        <p>{text}</p>
        <CTAButton href="/book-consultation" event="consultation_cta_clicked">{cta}</CTAButton>
      </div>
    </section>
  );
}
