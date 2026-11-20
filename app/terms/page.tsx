import type { Metadata } from "next";
import Link from "next/link";
import PageHero from "@/components/common/PageHero";
export const metadata: Metadata = { title: "Terms of Use" };
export default function Terms() {
  return (
    <>
      <PageHero title="Terms of Use" />
      <section className="section"><div className="container legal-page" style={{ maxWidth: 800 }}>
        <div className="note-box"><strong>Draft for legal review.</strong> Placeholder text to be replaced with terms reviewed by qualified counsel before launch.</div>
        <h2>General information only</h2><p>Website content and any chat assistant responses are informational. They are not legal, accounting or compliance advice, and do not guarantee compliance, audit outcomes or funder approval.</p>
        <h2>Pricing</h2><p>Prices shown are indicative and subject to confirmation.</p>
        <h2>AI-generated content</h2><p>AI-assisted outputs require human review and must not be relied on for financial, contractual or compliance decisions.</p>
        <h2>Contact</h2><p>Questions can be sent through our <Link href="/contact">contact page</Link>.</p>
      </div></section>
    </>
  );
}
