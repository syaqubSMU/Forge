import type { Metadata } from "next";
import { PageHero } from "@/components/ui/Section";
import Section from "@/components/ui/Section";
import { DiscoveryForm } from "@/components/forms/ContactForm";
export const metadata: Metadata = { title: "Book a Discovery Call", description: "Request a discovery call to talk through your research operations with FORGE." };
export default function Book() {
  return (
    <>
      <PageHero eyebrow="Discovery call" title="Book a discovery call." text="Tell us a little about your team and portfolio. We will follow up to arrange a conversation. No obligation." />
      <Section tone="white">
        <div className="split split--form">
          <div className="panel form-shell"><DiscoveryForm /></div>
          <div className="stack">
            <div className="panel"><h3>What to expect</h3><ul className="checks"><li>A short conversation about your portfolio, team and current tools</li><li>Honest guidance on what would help, including when it is not FORGE</li><li>A suggested next step, with no pressure</li></ul></div>
            <p className="note">Please don&apos;t include confidential award documents or restricted data in this form.</p>
          </div>
        </div>
      </Section>
    </>
  );
}
