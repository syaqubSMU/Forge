import type { Metadata } from "next";
import { PageHero } from "@/components/ui/Section";
import Section from "@/components/ui/Section";
export const metadata: Metadata = { title: "Terms of Use" };
export default function Terms() {
  return (<><PageHero title="Terms of Use" /><Section tone="white"><div className="article">
    <p className="note"><b>Draft for legal review.</b> Placeholder text to be replaced with terms reviewed by qualified counsel before launch.</p>
    <h2>General information only</h2><p>Website content and tools are informational. They are not legal, accounting or compliance advice and do not guarantee compliance or any outcome.</p>
    <h2>Not an accounting system</h2><p>FORGE is an operational monitoring and intelligence layer. It is not an institutional accounting system and does not replace official institutional records.</p>
    <h2>Illustrative content</h2><p>Product screens use illustrative synthetic data. Prices are indicative and subject to confirmation.</p>
    <h2>AI-generated content</h2><p>AI-assisted output requires human review and must not be relied on for financial, contractual or compliance decisions.</p></div></Section></>);
}
