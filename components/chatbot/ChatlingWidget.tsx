"use client";
import { useEffect, useState } from "react";
import Script from "next/script";
import { MessageOutlined } from "@ant-design/icons";
import { site } from "@/lib/content";
import { track } from "@/lib/analytics";
import CTAButton from "../common/CTAButton";

/**
 * Chatling integration point.
 * - If NEXT_PUBLIC_CHATLING_CHATBOT_ID is set, loads Chatling's embed script (confirm the snippet against the
 *   one shown in the Forge Chatling dashboard before launch).
 * - Otherwise renders a clearly-labelled placeholder launcher so the position and behaviour can be reviewed.
 */
export default function ChatlingWidget() {
  const id = site.chatbotId;
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (id) (window as unknown as { chtlConfig?: unknown }).chtlConfig = { chatbotId: id };
  }, [id]);

  if (id) {
    return (
      <>
        <Script id="chtl-config" strategy="afterInteractive">{`window.chtlConfig = { chatbotId: "${id.replace(/[^a-zA-Z0-9_-]/g, "")}" }`}</Script>
        <Script id="chatling-embed-script" strategy="lazyOnload" src="https://chatling.ai/js/embed.js" data-id={id} />
      </>
    );
  }
  return (
    <>
      {open && (
        <section className="chat-panel" role="dialog" aria-label="Forge Assistant (placeholder)">
          <header>Forge Assistant <button onClick={() => setOpen(false)} aria-label="Close chat">×</button></header>
          <div className="chat-body">
            <div className="bubble">{site.chatWelcome}</div>
            <div className="note-box">
              <strong>Chatbot placeholder.</strong> The live Chatling.ai assistant is not connected yet. Set <code>NEXT_PUBLIC_CHATLING_CHATBOT_ID</code> to activate it.
            </div>
            <CTAButton href="/contact" tone="secondary" block>Contact Forge instead</CTAButton>
          </div>
        </section>
      )}
      <button className="chat-fab" aria-expanded={open} onClick={() => { setOpen(!open); if (!open) track("chatbot_opened", { placeholder: true }); }}>
        <MessageOutlined /> Ask Forge
      </button>
    </>
  );
}
