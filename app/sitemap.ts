import type { MetadataRoute } from "next";
import { products, articles } from "@/lib/content";
import { siteUrl, basePath } from "@/lib/path";
export const dynamic = "force-static";
export default function sitemap(): MetadataRoute.Sitemap {
  const base = `${siteUrl}${basePath}`;
  const pages = ["", "/platform/", "/solutions/", "/products/", "/ai-automation/", "/insights/", "/about/", "/contact/", "/book-discovery-call/", "/privacy/", "/terms/"];
  return [...pages.map((p) => `${base}${p || "/"}`), ...products.map((p) => `${base}/products/${p.slug}/`), ...articles.map((a) => `${base}/insights/${a.slug}/`)].map((url) => ({ url }));
}
