"use client";
import { Collapse } from "antd";
export default function FAQAccordion({ items }: { items: { q: string; a: string }[] }) {
  return (
    <Collapse
      accordion
      bordered={false}
      style={{ background: "#fff", border: "1px solid #E2E0DA" }}
      items={items.map((f, i) => ({ key: String(i), label: <strong>{f.q}</strong>, children: <p style={{ margin: 0 }}>{f.a}</p> }))}
    />
  );
}
