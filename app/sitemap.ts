import type { MetadataRoute } from "next";
import { products } from "@/lib/content";
import { siteUrl, basePath } from "@/lib/path";
export const dynamic = "force-static";
export default function sitemap(): MetadataRoute.Sitemap {
  const base = `${siteUrl}${basePath}`;
  const pages = ["", "/products/", "/ai-automation/"];
  return [...pages.map((p) => `${base}${p || "/"}`), ...products.map((p) => `${base}/products/${p.slug}/`)].map((url) => ({ url }));
}
