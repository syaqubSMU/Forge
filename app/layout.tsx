import type { Metadata } from "next";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { ConfigProvider } from "antd";
import { Manrope } from "next/font/google";
import { theme } from "@/lib/theme";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import ChatlingWidget from "@/components/chatbot/ChatlingWidget";
import "./globals.css";

const sans = Manrope({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  title: { default: "Forge — Better Systems. Stronger Grant Operations.", template: "%s | Forge" },
  description: "Forge helps nonprofits build the systems, financial controls, compliance workflows and technology needed to manage grant-funded programs effectively.",
  icons: { icon: `${process.env.NEXT_PUBLIC_BASE_PATH || ""}/logo.webp` },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={sans.variable}>
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
