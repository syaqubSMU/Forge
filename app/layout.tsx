import type { Metadata } from "next";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { ConfigProvider } from "antd";
import { Inter, Space_Grotesk, Sora, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import { theme } from "@/lib/theme";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChatlingWidget from "@/components/chatbot/ChatlingWidget";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const space = Space_Grotesk({ subsets: ["latin"], variable: "--font-head", display: "swap", weight: ["500", "600", "700"] });
const sora = Sora({ subsets: ["latin"], variable: "--font-sora", display: "swap", weight: ["600", "700", "800"] });
const plex = IBM_Plex_Sans({ subsets: ["latin"], variable: "--font-num", display: "swap", weight: ["500", "600"], style: ["normal"] });
const mono = IBM_Plex_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap", weight: ["400", "500", "600"] });

export const metadata: Metadata = {
  title: { default: "Forge — Better Systems. Stronger Grant Operations.", template: "%s | Forge" },
  description: "Forge helps nonprofits build the systems, financial controls, compliance workflows and technology needed to manage grant-funded programs effectively.",
  icons: { icon: `${process.env.NEXT_PUBLIC_BASE_PATH || ""}/logo.webp` },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${space.variable} ${sora.variable} ${plex.variable} ${mono.variable}`}>
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
