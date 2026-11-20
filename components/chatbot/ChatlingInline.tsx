"use client";
import { useEffect, useRef } from "react";
import { track } from "@/lib/analytics";

/**
 * Chatling "page_inline" embed, mirroring the official snippet:
 *   window.chtlConfig = { chatbotId, display: "page_inline" }
 *   <div id="chtl-inline-bot" style="width:100%;height:500px"></div>
 *   <script async data-id=... data-display="page_inline" id="chtl-script" src="https://chatling.ai/js/embed.js">
 * The container and script are created imperatively inside an EMPTY React-owned host, so Chatling's DOM changes
 * can never conflict with React's own rendering (which causes "client-side exception" errors).
 */
export default function ChatlingInline({ botId }: { botId: string }) {
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = host.current;
    if (!el || !botId) return;
    let script: HTMLScriptElement | null = null;
    let box: HTMLDivElement | null = null;
    try {
      box = document.createElement("div");
      box.id = "chtl-inline-bot";
      box.style.cssText = "width:100%;height:500px";
      el.appendChild(box);
      (window as unknown as { chtlConfig?: unknown }).chtlConfig = { chatbotId: botId, display: "page_inline" };
      document.getElementById("chtl-script")?.remove();
      script = document.createElement("script");
      script.async = true; script.id = "chtl-script"; script.type = "text/javascript";
      script.setAttribute("data-id", botId); script.setAttribute("data-display", "page_inline");
      script.src = "https://chatling.ai/js/embed.js";
      script.onload = () => track("chatbot_opened", { inline: true, tool: "travel-calculator" });
      document.body.appendChild(script);
    } catch { /* never let a third-party widget break the page */ }
    return () => {
      try { script?.remove(); box?.remove(); } catch { /* ignore */ }
    };
  }, [botId]);

  if (!botId) return <div className="note-box">This tool isn’t connected yet.</div>;
  return <div ref={host} role="region" aria-label="Travel Calculator" style={{ width: "100%", minHeight: 500 }} />;
}
