"use client";
import Script from "next/script";
import { site } from "@/lib/content";

/** Optional floating site assistant. Renders nothing unless NEXT_PUBLIC_CHATLING_CHATBOT_ID is set (no dead controls). */
export default function ChatlingWidget() {
  const id = site.chatbotId.replace(/[^a-zA-Z0-9_-]/g, "");
  if (!id) return null;
  return (<>
    <Script id="chtl-config" strategy="afterInteractive">{`window.chtlConfig = { chatbotId: "${id}" }`}</Script>
    <Script id="chatling-embed-script" strategy="lazyOnload" src="https://chatling.ai/js/embed.js" data-id={id} />
  </>);
}
