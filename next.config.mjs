// Static export for GitHub Pages. NEXT_PUBLIC_BASE_PATH is set by the deploy workflow (e.g. "/gos-website").
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
  images: { unoptimized: true },
  reactStrictMode: true,
  transpilePackages: ["antd", "@ant-design/icons"],
};
export default nextConfig;
