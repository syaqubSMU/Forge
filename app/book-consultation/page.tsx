import type { Metadata } from "next";
import PageHero from "@/components/common/PageHero";
import ConsultationForm from "@/components/forms/ConsultationForm";
import FormShell from "@/components/forms/FormShell";
export const metadata: Metadata = { title: "Book a Consultation", description: "Request a grant operations consultation." };
export default function Book() {
  return (
    <>
      <PageHero eyebrow="Consultation" title="Book a consultation." text="Share a few details so we can come prepared. Please don’t include confidential award documents or sensitive financial information." />
      <section className="section"><div className="container"><FormShell><ConsultationForm /></FormShell></div></section>
    </>
  );
}
