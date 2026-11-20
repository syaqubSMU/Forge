"use client";
import { useEffect } from "react";
import { Breadcrumb } from "antd";
import Link from "next/link";
import type { Product } from "@/lib/content";
import { track } from "@/lib/analytics";
import ProductMock from "./ProductMock";
import FAQAccordion from "../common/FAQAccordion";
import CTAButton from "../common/CTAButton";

export default function ProductDetails({ p }: { p: Product }) {
  useEffect(() => { track("product_viewed", { product: p.slug }); }, [p.slug]);
  return (
    <section className="section">
      <div className="container">
        <Breadcrumb style={{ marginBottom: 24 }} items={[{ title: <Link href="/products">Products</Link> }, { title: p.title }]} />
        <div className="card-grid grid-2" style={{ alignItems: "start" }}>
          <ProductMock label={p.title} />
          <div>
            <div className="eyebrow">{p.category}</div>
            <h1 style={{ fontSize: "clamp(28px,4vw,40px)" }}>{p.title}</h1>
            <p className="lead" style={{ margin: "12px 0" }}>{p.description}</p>
            <div className="price" style={{ margin: "12px 0" }}>{p.price} <small>indicative price</small></div>
            <CTAButton href={`/contact?interest=${encodeURIComponent(p.title)}`}>Request this product</CTAButton>
            <div className="note-box" style={{ marginTop: 14 }}>Online checkout is not live yet. This button sends a product inquiry to Forge.</div>
          </div>
        </div>
        <div className="card-grid grid-2" style={{ marginTop: 40 }}>
          <div className="gcard"><h3>What’s included</h3><ul>{p.includes.map((i) => <li key={i}>{i}</li>)}</ul></div>
          <div className="gcard"><h3>Intended for</h3><p>{p.audience}</p></div>
        </div>
        <h2 style={{ fontSize: 26, margin: "40px 0 16px" }}>Frequently asked questions</h2>
        <FAQAccordion items={p.faqs} />
      </div>
    </section>
  );
}
