import type { Metadata } from "next";
import { PageHero } from "@/components/ui/Section";
import Section from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import { GeneralForm } from "@/components/forms/ContactForm";
import { site } from "@/lib/content";
export const metadata: Metadata = { title: "Contact", description: "Get in touch with FORGE." };
export default function Contact() {
  return (
    <>
      <PageHero eyebrow="Contact" title="Get in touch." text="Send a general question, or book a discovery call to talk through your situation." />
      <Section tone="white">
        <div className="split split--form">
          <div className="panel form-shell"><GeneralForm /></div>
          <div className="stack">
            <div className="panel"><h3>Prefer a conversation?</h3><p>Book a discovery call to talk through your portfolio, team and systems.</p><div className="btn-row"><Button href="/book-discovery-call" event="consultation_cta_clicked">Book a Discovery Call</Button></div></div>
            <p><b>Email:</b> {site.contactEmail ? <a href={`mailto:${site.contactEmail}`}>{site.contactEmail}</a> : "A business email will be listed here soon."}</p>
          </div>
        </div>
      </Section>
    </>
  );
}
