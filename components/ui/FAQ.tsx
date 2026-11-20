"use client";
import { Collapse } from "antd";
export default function FAQ({ items }: { items: { q: string; a: string }[] }) {
  return <div className="faq"><Collapse accordion items={items.map((f, i) => ({ key: String(i), label: <strong>{f.q}</strong>, children: <p>{f.a}</p> }))} /></div>;
}
