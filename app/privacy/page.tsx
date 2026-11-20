import type { Metadata } from "next";
import { PageHero } from "@/components/ui/Section";
import Section from "@/components/ui/Section";
export const metadata: Metadata = { title: "Privacy Notice" };
export default function Privacy() {
  return (<><PageHero title="Privacy Notice" /><Section tone="white"><div className="article">
    <p className="note"><b>Draft for legal review.</b> Placeholder text to be reviewed and finalized before launch to reflect actual data practices and the actual data handling of third-party services (forms, analytics, chat tool).</p>
    <h2>Information we collect</h2><p>Information you submit through forms (name, work email, institution, role, message) and basic usage analytics.</p>
    <h2>How we use it</h2><p>To respond to inquiries, provide requested resources or services, and improve the website.</p>
    <h2>Please do not share sensitive information</h2><p>Do not submit confidential award documents or restricted data (for example health, financial account or student record information) through website forms or the free tools.</p>
    <h2>Third-party services</h2><p>The site may use third-party services such as an embedded calculator tool and analytics. Details will be listed here once finalized.</p>
    <h2>Contact</h2><p>Questions about this notice can be sent through the contact page.</p></div></Section></>);
}
