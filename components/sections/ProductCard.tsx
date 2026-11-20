import Link from "next/link";
import type { Product } from "@/lib/content";
import ProductVisual from "../ui/ProductVisual";
export default function ProductCard({ p }: { p: Product }) {
  return (
    <Link href={`/products/${p.slug}`} className="panel panel--link" aria-label={`${p.title}: ${p.blurb}`}>
      <ProductVisual kind={p.visual} label={p.title} />
      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginTop: 6 }}>
        <span className="num">{p.category}</span><span className={p.status === "Free tool" ? "badge badge--ok" : "badge"}>{p.status}</span>
      </div>
      <h3 style={{ margin: 0 }}>{p.title}</h3><p style={{ flex: 1 }}>{p.blurb}</p>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <b style={{ fontFamily: "var(--f-head)", fontSize: 20, color: "var(--blue)" }}>{p.price}</b><span className="link-arrow">View <span aria-hidden="true">→</span></span>
      </div>
    </Link>
  );
}
