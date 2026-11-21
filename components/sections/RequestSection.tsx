import Section, { SectionHeading } from "../ui/Section";
import { GeneralForm } from "../forms/ContactForm";
import { requestsOpen } from "@/lib/content";

/** Product request form. Hidden (replaced by a plain notice) until a form endpoint is configured, so nothing is submitted into a void. */
export default function RequestSection({ product }: { product?: string }) {
  return (
    <Section tone="soft" id="request">
      <SectionHeading eyebrow="Request" title={product ? `Request ${product}` : "Request a product"} text="Tell us which tool you need and a little about your team. We will follow up with delivery details." />
      {requestsOpen
        ? <div className="panel form-shell"><GeneralForm prefill={product ? `I'd like to request: ${product}` : undefined} /></div>
        : <p className="note" style={{ maxWidth: 720 }}>Online requests are opening soon. Online ordering is not available yet.</p>}
    </Section>
  );
}
