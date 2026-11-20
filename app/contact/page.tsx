import type { Metadata } from "next";
import PageHero from "@/components/common/PageHero";
import ContactForm from "@/components/forms/ContactForm";
import FormShell from "@/components/forms/FormShell";
import CTAButton from "@/components/common/CTAButton";
import { site } from "@/lib/content";
export const metadata: Metadata = { title: "Contact", description: "Get in touch with Forge." };
export default function Contact() {
  return (
    <>
      <PageHero eyebrow="Contact" title="Let’s talk about your grant operations." text="Send a general inquiry, or book a consultation if you’d like to discuss your specific situation." />
      <section className="section">
        <div className="container card-grid grid-2" style={{ alignItems: "start" }}>
          <FormShell><ContactForm /></FormShell>
          <div>
            <div className="gcard">
              <h3 style={{ marginTop: 0 }}>Prefer a consultation?</h3>
              <p>Tell us about your organization and challenges, and we’ll follow up.</p>
              <CTAButton href="/book-consultation" event="consultation_cta_clicked">Book a Consultation</CTAButton>
              <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "20px 0" }} />
              <p style={{ marginBottom: 6 }}><strong>Email:</strong> {site.contactEmail ? <a href={`mailto:${site.contactEmail}`}>{site.contactEmail}</a> : "Business email coming soon"}</p>
              {site.responseTime && <p style={{ margin: 0 }}>{site.responseTime}</p>}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
