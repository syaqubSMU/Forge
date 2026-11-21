import type { Metadata } from "next";
import { products } from "@/lib/content";
import Section, { PageHero } from "@/components/ui/Section";
import ProductCard from "@/components/sections/ProductCard";
import RequestSection from "@/components/sections/RequestSection";
export const metadata: Metadata = { title: "Products", description: "Practical research administration tools: Award Tracker, Budget Monitor, a free Travel Budget Calculator, Compliance Calendar, templates, SOP Library and toolkits." };
export default function Products() {
  return (
    <>
      <PageHero eyebrow="Products" title="Practical tools for research administration." text="Spreadsheet-based tools and templates you can use today, plus a free travel budget calculator. Prices are indicative." />
      <Section tone="white">
        <div className="grid g3">{products.map((p) => <ProductCard key={p.slug} p={p} />)}</div>
        <p className="note" style={{ marginTop: 32 }}>Online checkout is not available yet. Request a product and FORGE will follow up with delivery details. These tools support departmental monitoring and do not replace official institutional records.</p>
      </Section>
      <RequestSection />
    </>
  );
}
