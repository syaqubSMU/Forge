import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { products } from "@/lib/content";
import ProductDetails from "@/components/products/ProductDetails";
export const dynamicParams = false;
export const generateStaticParams = () => products.map((p) => ({ slug: p.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const p = products.find((x) => x.slug === params.slug);
  return { title: p?.title, description: p?.blurb };
}
export default function ProductPage({ params }: { params: { slug: string } }) {
  const p = products.find((x) => x.slug === params.slug);
  if (!p) notFound();
  return <ProductDetails p={p} />;
}
