"use client";
import { useState } from "react";
import Link from "next/link";
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

  if (id) {
    // Chat is embedded inline on the Contact page; the floating button takes visitors to it.
    return (
      <Link className="chat-fab" href="/contact/#chat" onClick={() => track("chatbot_opened", { from: "fab" })}>
        <MessageOutlined /> Ask Forge
      </Link>
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
