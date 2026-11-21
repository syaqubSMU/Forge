"use client";
import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import Script from "next/script";
import { site } from "@/lib/content";

const CALC = "travel-budget-calculator";

/**
 * Site-wide Forge assistant (Chatling floating widget). Renders nothing until NEXT_PUBLIC_CHATLING_CHATBOT_ID is set.
 * It is skipped on the Travel Budget Calculator page, which embeds a different Chatling bot inline; two bots on one
 * page would share Chatling's global config. Moving between that page and the rest of the site does a full page load
 * so each bot starts from a clean state.
 */
export default function ChatlingWidget() {
  const id = site.chatbotId.replace(/[^a-zA-Z0-9_-]/g, "");
  const path = usePathname() || "";
  const onCalc = path.includes(CALC);
  const prev = useRef(onCalc);
  useEffect(() => {
    if (prev.current !== onCalc) { prev.current = onCalc; if (id) window.location.reload(); }
  }, [onCalc, id]);
  if (!id || onCalc) return null;
  return (<>
    <Script id="chtl-config" strategy="afterInteractive">{`window.chtlConfig = { chatbotId: "${id}" }`}</Script>
    <Script id="chatling-embed-script" strategy="lazyOnload" src="https://chatling.ai/js/embed.js" data-id={id} />
  </>);
}
