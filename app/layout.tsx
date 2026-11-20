import type { Metadata, Viewport } from "next";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { ConfigProvider } from "antd";
import { Sora, Inter, IBM_Plex_Mono } from "next/font/google";
import { theme } from "@/lib/theme";
import { siteUrl } from "@/lib/path";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChatlingWidget from "@/components/chatbot/ChatlingWidget";
import "./globals.css";

const head = Sora({ subsets: ["latin"], variable: "--font-head", display: "swap", weight: ["500", "600", "700"] });
const body = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap", weight: ["400", "500"] });

const description = "FORGE is a connected research operations workspace for small research administration teams: grants, budgets, compliance and documents in one place, working alongside your university systems.";
export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: "FORGE — Connected research operations. Research administration, made simpler.", template: "%s | FORGE" },
  description,
  openGraph: { type: "website", siteName: "FORGE", title: "FORGE — Connected research operations", description: "Research administration, made simpler.", locale: "en_US" },
  twitter: { card: "summary_large_image", title: "FORGE — Connected research operations", description: "Research administration, made simpler." },
  robots: { index: true, follow: true },
};
export const viewport: Viewport = { themeColor: "#244B70", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${head.variable} ${body.variable} ${mono.variable}`}>
      <body>
        <a className="skip-link" href="#main">Skip to main content</a>
        <AntdRegistry>
          <ConfigProvider theme={theme}>
            <Header />
            <main id="main">{children}</main>
            <Footer />
            <ChatlingWidget />
          </ConfigProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
