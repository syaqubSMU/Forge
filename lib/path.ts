/** Prefix root-relative asset/anchor URLs with the GitHub Pages base path (Link/router handle it automatically). */
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
export const withBase = (href: string) => (href.startsWith("/") ? basePath + href : href);
