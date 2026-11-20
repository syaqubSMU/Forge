/** Prefix root-relative asset URLs with the GitHub Pages base path (Link/router handle it automatically). */
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
export const withBase = (href: string) => (href.startsWith("/") ? basePath + href : href);
export const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://syaqubsmu.github.io";
