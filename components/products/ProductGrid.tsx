"use client";
import { useState } from "react";
import { Tabs } from "antd";
import { products, productCategories } from "@/lib/content";
import ProductCard from "./ProductCard";
export default function ProductGrid() {
  const [cat, setCat] = useState("All");
  const shown = cat === "All" ? products : products.filter((p) => p.category === cat);
  const tabs = ["All", ...productCategories.filter((c) => products.some((p) => p.category === c))];
  return (
    <>
      <Tabs activeKey={cat} onChange={setCat} items={tabs.map((t) => ({ key: t, label: t }))} />
      <div className="card-grid grid-3">{shown.map((p) => <ProductCard key={p.slug} p={p} />)}</div>
    </>
  );
}
