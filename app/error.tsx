"use client";
import { useEffect } from "react";
import Link from "next/link";

/** Friendly fallback so a runtime error never shows the bare "Application error" screen. */
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return (
    <section className="section">
      <div className="container" style={{ maxWidth: 640, textAlign: "center" }}>
        <h1 style={{ fontSize: 32 }}>Something went wrong.</h1>
        <p className="lead" style={{ margin: "12px auto 24px" }}>This page hit a problem loading. Please try again, or head back to the homepage.</p>
        <div className="cta-row" style={{ justifyContent: "center" }}>
          <button className="btn-shine ant-btn" style={{ padding: "12px 22px", cursor: "pointer", borderRadius: 10, fontWeight: 600, fontSize: 16 }} onClick={() => reset()}>Try again</button>
          <Link href="/" style={{ alignSelf: "center", fontWeight: 600 }}>Back to home</Link>
        </div>
      </div>
    </section>
  );
}
