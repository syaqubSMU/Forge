import Section, { SectionHeading } from "../ui/Section";
import { GeneralForm } from "../forms/ContactForm";
import { requestsOpen } from "@/lib/content";

/** Product request form. Hidden (replaced by a plain notice) until a form endpoint is configured, so nothing is submitted into a void. */
export default function RequestSection({ product }: { product?: string }) {
  return (
    <Section tone="soft" id="request">
      <SectionHeading eyebrow="Request" title={product ? `Request a demo of ${product}` : "Request a demo"} text="Tell us which tool you would like to see and a little about your team. We will follow up to arrange a demo." />
      {requestsOpen
        ? <div className="panel form-shell"><GeneralForm prefill={product ? `I'd like a demo of: ${product}` : undefined} /></div>
        : <p className="note" style={{ maxWidth: 720 }}>Demo requests are opening soon. Online ordering is not available yet.</p>}
    </Section>
  );
}
