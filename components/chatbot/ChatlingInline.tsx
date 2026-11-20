"use client";
import { useEffect } from "react";
import { track } from "@/lib/analytics";

/**
 * Chatling "page_inline" embed, mirroring the official snippet:
 *   window.chtlConfig = { chatbotId, display: "page_inline" }
 *   <div id="chtl-inline-bot" style="width:100%;height:500px"></div>
 *   <script async data-id=... data-display="page_inline" id="chtl-script" src="https://chatling.ai/js/embed.js">
 * The script is (re)inserted on mount so the chat also appears after client-side navigation.
 */
export default function ChatlingInline({ botId }: { botId: string }) {
  const id = botId;
  useEffect(() => {
    if (!id) return;
    const w = window as unknown as { chtlConfig?: unknown };
    w.chtlConfig = { chatbotId: id, display: "page_inline" };
    document.getElementById("chtl-script")?.remove();
    const s = document.createElement("script");
    s.async = true; s.id = "chtl-script"; s.type = "text/javascript";
    s.setAttribute("data-id", id); s.setAttribute("data-display", "page_inline");
    s.src = "https://chatling.ai/js/embed.js";
    s.onload = () => track("chatbot_opened", { inline: true, tool: "travel-calculator" });
    document.body.appendChild(s);
    return () => { s.remove(); const c = document.getElementById("chtl-inline-bot"); if (c) c.innerHTML = ""; };
  }, [id]);

  if (!id) return <div className="note-box">This tool isn’t connected yet.</div>;
  return <div id="chtl-inline-bot" style={{ width: "100%", height: 500 }} aria-label="Travel Calculator" />;
}
