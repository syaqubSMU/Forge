import { products } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
import CTAButton from "../common/CTAButton";
import ProductMock from "../products/ProductMock";
export default function FeaturedProduct() {
  const p = products.find((x) => x.slug === "complete-grant-operations-toolkit")!;
  return (
    <section className="section section--white">
      <div className="container">
        <SectionHeading eyebrow="Featured product" title="Start Building Your Grant Operations System." />
        <div className="feature-grid">
          <ProductMock label={p.title} />
          <div>
            <h3 style={{ fontSize: 26 }}>Forge Grant Operations Toolkit</h3>
            <p className="lead" style={{ margin: "10px 0 14px" }}>{p.description}</p>
            <ul style={{ paddingLeft: 18, lineHeight: 1.8 }}>{p.includes.map((i) => <li key={i}>{i}</li>)}</ul>
            <div className="price" style={{ margin: "14px 0" }}>{p.price} <small>indicative price</small></div>
            <CTAButton href={`/products/${p.slug}`}>View the Toolkit</CTAButton>
          </div>
        </div>
      </div>
    </section>
  );
}
