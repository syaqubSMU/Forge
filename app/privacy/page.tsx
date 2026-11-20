import type { Metadata } from "next";
import Link from "next/link";
import PageHero from "@/components/common/PageHero";
export const metadata: Metadata = { title: "Privacy Notice" };
export default function Privacy() {
  return (
    <>
      <PageHero title="Privacy Notice" />
      <section className="section"><div className="container legal-page" style={{ maxWidth: 800 }}>
        <div className="note-box"><strong>Draft for legal review.</strong> This is placeholder text and must be reviewed and finalized before launch to reflect Forge’s actual data practices and the actual data-handling of third-party services (chatbot, analytics, payments, CRM).</div>
        <h2>Information we collect</h2><p>Information you submit through forms (such as name, work email, organization, role and your message) and basic usage analytics.</p>
        <h2>How we use it</h2><p>To respond to inquiries, provide requested resources or services, and improve the website.</p>
        <h2>Please don’t share sensitive documents</h2><p>Do not submit confidential award documents or sensitive financial information through the website forms or public chat.</p>
        <h2>Third-party services</h2><p>The site may use third-party services such as a chat assistant, analytics and payment processors. Details will be listed here once those services are finalized.</p>
        <h2>Contact</h2><p>Questions about this notice can be sent through our <Link href="/contact">contact page</Link>.</p>
      </div></section>
    </>
  );
}
