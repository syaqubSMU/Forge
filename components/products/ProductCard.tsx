import Link from "next/link";
import type { Product } from "@/lib/content";
import ProductMock from "./ProductMock";
export default function ProductCard({ p }: { p: Product }) {
  return (
    <article className="gcard">
      <ProductMock label={p.title} />
      <div className="eyebrow" style={{ marginTop: 10 }}>{p.category}</div>
      <h3 style={{ marginTop: 0 }}>{p.title}</h3><p>{p.blurb}</p>
      <div className="price">{p.price}</div>
      <Link className="more" href={`/products/${p.slug}`} aria-label={`View ${p.title}`}>View details →</Link>
    </article>
  );
}
