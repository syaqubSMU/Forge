import type { Metadata } from "next";
import PageHero from "@/components/common/PageHero";
import ProductGrid from "@/components/products/ProductGrid";
import FinalCTA from "@/components/common/FinalCTA";
export const metadata: Metadata = { title: "Products", description: "Downloadable grant management templates, trackers and toolkits." };
export default function Products() {
  return (
    <>
      <PageHero eyebrow="Products" title="Ready-to-use grant operations toolkits." text="Downloadable digital products to help small teams get organized quickly. Prices shown are indicative." />
      <section className="section"><div className="container"><ProductGrid /></div></section>
      <FinalCTA title="Not sure which product fits?" text="Tell us about your grant portfolio and we'll point you to the right starting point." />
    </>
  );
}
